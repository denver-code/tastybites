from typing import Dict
from pydantic import BaseModel, Field

from models.database import *

announce_collection = database["announce"]
announce_directory = "Announces"


class AnnounceLang(BaseModel):
    title: str = 'title'
    description: str = 'description'


class Announce(BaseModel):
    id: int = Field(None, alias='_id')

    image: str = f'objects/{announce_directory}/default.jpg'
    language: Dict[str, AnnounceLang] = {'uk': AnnounceLang(), 'en': AnnounceLang()}
    isShow: bool = True

    def from_form(self, form, image):

        if image:
            self.image = save_image(image, announce_directory, self.id)

        self.language = {
            "uk": AnnounceLang(title=form["uk_title"], description=form["uk_description"]),
            "en": AnnounceLang(title=form["en_title"], description=form["en_description"]),
        }
        self.isShow = form["isShow"]

        return self

    def save(self):
        if document_by_id(announce_collection, self.id):
            announce_collection.replace_one({'_id': self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(announce_collection)
            announce_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        delete_image(announce_directory, self.id)
        announce_collection.delete_one({'_id': self.id})
