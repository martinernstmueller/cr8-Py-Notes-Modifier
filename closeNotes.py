from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime, timedelta
import argparse

parser = argparse.ArgumentParser(
    description="Modify Notes"
)
parser.add_argument("notes_url", help="url to notes service")
    
parser.add_argument(
        "--access_token",
        type=str,
        help="access token to connect to notes service",
    )
args = parser.parse_args()

requestHeaders = {
    'Authorization': 'Bearer ' + args.access_token
}

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url=args.notes_url + "/v2/gql", headers=requestHeaders)

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
			"value": "2022-11-01"
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
        "status": "CLOSED"
        }
      }
      if (note['type'] == 'CheckResultNote'):
        result = client.execute(updateCheckResultNoteStatus, variable_values=closeparams)
      if (note['type'] == 'CustomNote'):
        result = client.execute(updateCustomNoteStatus, variable_values=closeparams)  
      if (note['type'] == 'CheckResultStreamNote'):
        result = client.execute(updateCheckResultNoteStatus, variable_values=closeparams)  
        
      print(note['id'] + ' closed')
  result = client.execute(getNotes, variable_values=getparams)
    
# datetime.fromtimestamp(created/1000.0)
# created = result['notes']['data'][0]['dc']['created']
print(result)