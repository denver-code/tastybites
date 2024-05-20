from typing import Dict
from pydantic import BaseModel, Field

from models.database import *

settings_collection = database["settings"]


class SettingsLang(BaseModel):
    name: str = "name"
    description: str = "description"
    address: str = "address"


class Settings(BaseModel):
    id: int = Field(1, alias="_id")

    email: str = "default@gmail.com"
    language: Dict[str, SettingsLang] = {"uk": SettingsLang(), "en": SettingsLang()}

    instagram: str = "https://instagram.com/"
    facebook: str = "https://facebook.com/"
    tiktok: str = "https://tiktok.com/"

    phone_1: str = "+44 999 99 99 99"
    phone_2: str = "+44 999 99 99 99"

    monday_time: str = "monday_time"
    other_days_time: str = "other_days_time"

    def from_form(self, form):

        self.email = form["email"]
        self.language = {
            "uk": SettingsLang(
                name=form["uk_name"],
                description=form["uk_description"],
                address=form["uk_address"],
            ),
            "en": SettingsLang(
                name=form["en_name"],
                description=form["en_description"],
                address=form["en_address"],
            ),
        }

        self.instagram = form["instagram"]
        self.facebook = form["facebook"]
        self.tiktok = form["tiktok"]

        self.phone_1 = form["phone_1"]
        self.phone_2 = form["phone_2"]

        self.monday_time = form["time_1"]
        self.other_days_time = form["time_2"]

        return self

    def save(self):
        if document_by_id(settings_collection, self.id):
            settings_collection.replace_one({"_id": self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(settings_collection)
            settings_collection.insert_one(self.dict(by_alias=True))
