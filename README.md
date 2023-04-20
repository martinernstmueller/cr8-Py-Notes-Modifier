# cr8-Py-Notes-Modifier
## Modifies a note via gql

This repository contains several Python-scripts which allows to modify (e.g. close) a note.

### Close a note
You can use the script `closeNotes.py` to set the status of a note to `closed`...

... to be continued if the repo should be moved to an official place...

python closeNotes.py https://controldev.missionj.com/noites-api --access_token='bearer token'

### run the script in a container on kubernetes:
`k apply -f manifest.yaml --namespace alpla-staging`

and delete the pod after running with
`k delete pod closenotes-pod  --namespace alpla-staging`

Delete notes from DB which are older as x days:
- create a timestamp to fetch them from the db: 
  `int(datetime.timestamp(datetime.today()  - timedelta(days=x))*1000)`
- query them to double check:
  `select * from "doc"."v2_notes" where dc['created'] > 1679402175830 limit 100;`
  `select count(*) from "doc"."v2_notes" where dc['created'] > 1679402175830;`
- delete notes older than `timestamp`
  `delete from "doc"."v2_notes" where dc['created'] < timestamp;`
  
