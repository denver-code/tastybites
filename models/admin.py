from typing import Dict

from flask_login import UserMixin
from pydantic import BaseModel, Field
from werkzeug.security import generate_password_hash
from models.database import *

admin_collection = database["admin"]


class Admin(UserMixin, BaseModel):
    id: int = Field(None, alias='_id')

    # data
    username: str = 'username'
    password: str = 'username'
    email: str = 'default@gmail.com'

    # Real names
    name: str = 'name'
    lastname: str = 'lastname'
    surname: str = 'surname'

    def from_form(self, form):

        self.username = form['username']
        self.email = form['email']

        if form['password']:
            self.password = generate_password_hash(form['password'], 'sha256')

        self.name = form['name']
        self.lastname = form['lastname']
        self.surname = form['surname']

        return self

    def save(self):
        if document_by_id(admin_collection, self.id):
            admin_collection.replace_one({'_id': self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(admin_collection)
            admin_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        admin_collection.delete_one({'_id': self.id})
