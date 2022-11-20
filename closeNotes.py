from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime, timedelta
import argparse
import os

notesGQLPath = ''

try:
  notesGQLPath = os.environ['notesGQLPath']
except:
  print('notesGQLPath not found in env variables... try to get it via arguments...')

notesBearerToken = ''
try:
  notesBearerToken = os.environ['notesBearerToken']
except:
  print('notesBearerToken not found in env variables... try to get it via arguments...')

notesKeepOpenDate = ''
try:
  notesKeepOpenDate = os.environ['notesKeepOpenDate']
except:
  print('notesKeepOpenDate not found in env variables... try to get it via arguments...')

parser = argparse.ArgumentParser(
    description="Modify Notes"
)
if (notesGQLPath == ''):
  parser.add_argument("notes_url", help="url to notes service")
    
if (notesBearerToken == ''):
  parser.add_argument(
        "--access_token",
        type=str,
        help="access token to connect to notes service",
    )

args = parser.parse_args()
if (notesBearerToken == ''):
  notesBearerToken = args.access_token

if (notesKeepOpenDate == ''):
  parser.add_argument(
        "--notes_open_date",
        type=str,
        help="timestamp until which notes should be hold open (== should not be closed)",
    )

# if we still dont have a timestamp until which we shuold close notes, we take today - 7 days
if (notesKeepOpenDate == ''):
  notesKeepOpenDate = str((datetime.now() - timedelta(days=7)).date())


if (notesGQLPath == ''):
  notesGQLPath = args.notes_url

requestHeaders = {
    'Authorization': 'Bearer ' + notesBearerToken
}

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url=notesGQLPath + "/v2/gql", headers=requestHeaders)

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)
updateCheckResultNoteStatus = gql(
  """
  mutation UpdateCheckResultNote($input: UpdateCheckResultNoteInput!) {
    updateCheckResultNote(input: $input) {
      status
    }
  }
  """
)

updateCustomNoteStatus = gql(
  """
  mutation UpdateCustomNote($input: UpdateCustomNoteInput!) {
    updateCustomNote(input: $input) {
      status
    }
  }
  """
)

updateCheckResultStreamStatus = gql(
  """
  mutation UpdateCheckResultStreamNote($input: UpdateCheckResultStreamNoteInput!) {
    updateCheckResultStreamNote(input: $input) {
      status
    }
  }
  """
)

getNotes = gql(
  """
  query AvailableNotes(
    $limit: Int,
    $sort: [NoteSortEnum],
    $filter: [NoteFilter]) {
    notes(
      limit: $limit,
      sort: $sort,
      filter: $filter
    ) {
      total
      data {
        ... on CheckResultNote {
					id
					dc {
						created
						modified
					}
        }
        ... on CustomNote {
					id
					dc {
						created
						modified
					}
        }
        ... on CheckResultStreamNote {
					id
					dc {
						created
						modified
					}
        }
        name
        status
        type
      }
    }
  }
  """
)
getparams = { 
  "limit": 100,
  "filter": [
		{
      "or": [
      {
        "by": "STATUS",
        "op": "EQ",
        "value": "NEW"
      },
      {
        "by": "STATUS",
        "op": "EQ",
        "value": "IN_PROGRESS"
      }]},
    {
			"by": "MODIFIED",
			"op": "LT",
			"value": notesKeepOpenDate
		},
    ],
	"sort": ["MODIFIED"]
  }
	

result = client.execute(getNotes, variable_values=getparams)
while len(result['notes']['data']) > 10:
  for note in result['notes']['data']:
    if (not 'dc' in note):
      continue
    modified = datetime.fromtimestamp(note['dc']['modified']/1000.0)
    nowMin7D = datetime.today()  - timedelta(days=7)
    
    if (modified < nowMin7D and note['status'] != 'CLOSED'):
      closeparams = { "input": {
        "id": note['id'],
        "status": "CLEANUP_CLOSED"
        }
      }
      try:
        if (note['type'] == 'CheckResultNote'):
          result = client.execute(updateCheckResultNoteStatus, variable_values=closeparams)
        if (note['type'] == 'CustomNote'):
          result = client.execute(updateCustomNoteStatus, variable_values=closeparams)  
        if (note['type'] == 'CheckResultStreamNote'):
          result = client.execute(updateCheckResultNoteStatus, variable_values=closeparams)  
        print(note['id'] + ' closed')
      except Exception:  
        print(note['id'] + ' could not be closed. Status still is ' + note['status'])
  result = client.execute(getNotes, variable_values=getparams)
    
# datetime.fromtimestamp(created/1000.0)
# created = result['notes']['data'][0]['dc']['created']
print(result)