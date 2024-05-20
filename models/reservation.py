from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field

from models.database import *

reservation_collection = database["reservation"]


class Reservation(BaseModel):
    id: int = Field(None, alias='_id')

    client_name: str = 'title'
    client_phone: str = 'title'
    client_comment: str = 'title'

    people_count: int = 1
    date: str = 'default_date'

    isAccepted: bool = False
    sentAt: str = datetime.now().strftime("%m/%d/%Y, %H:%M")

    def from_form(self, form):
        self.client_name = form['name']
        self.client_phone = form['phone']
        self.client_comment = form['comment']

        self.people_count = form['persons']
        self.date = form['date'] + ', ' + form['time']

        return self

    def save(self):
        if document_by_id(reservation_collection, self.id):
            reservation_collection.replace_one({'_id': self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(reservation_collection)
            self.sentAt = datetime.now().strftime("%m/%d/%Y, %H:%M")
            reservation_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        reservation_collection.delete_one({'_id': self.id})
