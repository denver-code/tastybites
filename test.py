import json

from models.announce import document_by_id, Announce, ann

a = Announce(**document_by_id(11))

data = json.loads('{}')
print(type(data))
