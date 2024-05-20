import os
import json
import random
import shutil
from enum import Enum
import string
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

from typing import Dict
from pydantic import BaseModel, Field

from models.database import *

dish_collection = database["dish"]
dish_category_collection = database["dish_category"]
dish_category_type_collection = database["category_type"]
dish_directory = "Dish"


class UKCategoryType(Enum):
    Restaurant = "Ресторан"
    Banquet = "Банкет"
    Souvenirs = "Сувеніри"

    Food = "Їжа"
    VineCard = "Винна карта"
    Drinks = "Напої"


class ENCategoryType(Enum):
    Restaurant = "Restaurant"
    Banquet = "Banquet"
    Souvenirs = "Souvenirs"

    Food = "Food"
    VineCard = "Vine сard"
    Drinks = "Drinks"


class DishCategoryLang(BaseModel):
    name: str = "name"


class DishLang(BaseModel):
    name: str = "name"
    ingredients: str = "-"
    description: str = "-"


class CategoryType(BaseModel):
    id: int = Field(None, alias="_id")

    uk_type: str = UKCategoryType.Restaurant.value
    en_type: str = UKCategoryType.Restaurant.value


class DishCategory(BaseModel):
    id: int = Field(None, alias="_id")

    language: Dict[str, DishCategoryLang] = {
        "uk": DishCategoryLang(),
        "en": DishCategoryLang(),
    }

    type: list = []
    code_name: str = "".join(random.choice(string.ascii_letters) for i in range(10))
    isShow: bool = True

    def from_form(self, form):

        if form["type"]:
            types = list(form["type"].split(","))
            self.type = [int(x) for x in types]

        self.language = {
            "uk": DishCategoryLang(name=form["uk_name"]),
            "en": DishCategoryLang(name=form["en_name"]),
        }
        self.code_name = form["code_name"]
        self.isShow = form["isShow"]

        return self

    def save(self):
        if document_by_id(dish_category_collection, self.id):
            dish_category_collection.replace_one(
                {"_id": self.id}, self.dict(by_alias=True)
            )
        else:
            self.id = new_document_id(dish_category_collection)
            dish_category_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        dish_category_collection.delete_one({"_id": self.id})

    @property
    def getDishCount(self):
        return len(list(dish_collection.find({"category": self.id})))

    @property
    def to_dict(self):
        data = self.dict()

        # data["type"] = [
        #     document_by_id(dish_category_type_collection, x)["uk_type"]
        #     for x in data["type"]
        # ]

        # data.update({"count": self.getDishCount})
        return data


class Dish(BaseModel):
    id: int = Field(None, alias="_id")
    category: int = 85

    image: str = f"objects/{dish_directory}/default.jpg"
    language: Dict[str, DishLang] = {"uk": DishLang(), "en": DishLang()}

    weight: str = "0"
    price: int = 0

    code_name: str = "".join(random.choice(string.ascii_letters) for i in range(10))
    isShow: bool = True
    isCm: bool = False

    def from_form(self, form, image):
        if image:
            self.image = save_image(image, dish_directory, self.id)

        self.language = {
            "uk": DishLang(
                name=form["uk_name"],
                ingredients=form["uk_ingredients"],
                description=form["uk_description"],
            ),
            "en": DishLang(
                name=form["en_name"],
                ingredients=form["en_ingredients"],
                description=form["en_description"],
            ),
        }
        self.category = int(form["category"])
        self.weight = form["weight"]
        self.price = form["price"]
        self.code_name = form["code_name"]
        self.isShow = form["isShow"]

        return self

    def save(self):
        if document_by_id(dish_collection, self.id):
            dish_collection.replace_one({"_id": self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(dish_collection)
            dish_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        delete_image(dish_directory, self.id)
        dish_collection.delete_one({"_id": self.id})
