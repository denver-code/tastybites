from typing import Dict
from pydantic import BaseModel, Field

from models.database import *

slider_collection = database["slider"]
slider_directory = "Slider"


class SliderLang(BaseModel):
    text: str = "TastyBites"


class Slider(BaseModel):
    id: int = Field(None, alias="_id")

    image: str = f"objects/{slider_directory}/default.jpg"
    language: Dict[str, SliderLang] = {"uk": SliderLang(), "en": SliderLang()}

    isShow: bool = True

    def from_form(self, form, image):

        if image:
            self.image = save_image(image, slider_directory, self.id)

        self.language = {
            "uk": SliderLang(text=form["uk_text"]),
            "en": SliderLang(text=form["en_text"]),
        }
        self.isShow = form["isShow"]

        return self

    def save(self):
        if document_by_id(slider_collection, self.id):
            slider_collection.replace_one({"_id": self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(slider_collection)
            slider_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        delete_image(slider_directory, self.id)
        slider_collection.delete_one({"_id": self.id})
