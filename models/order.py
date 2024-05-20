import json
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from models.database import database, new_document_id, document_by_id, delete_image

order_collection = database["order"]


class Status(Enum):
    CANCELED = "canceled"
    NEW = "new"
    ONGOING = "ongoing"
    DONE = "done"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, Status))


class Order(BaseModel):
    id: int = Field(None, alias="_id")

    cart: dict = {}

    client_email: str = "default@gmail.com"
    client_name: str = "default_name"
    client_phone: str = "+440 999 99 99 99"
    client_comment: str = "-"
    delivery: bool = True

    street: str = "-"
    house: str = "-"
    flat: str = "-"

    porch: str = "-"

    total: int = 0

    sentAt: str = datetime.now().strftime("%m/%d/%Y, %H:%M")
    date: str = "default_date"
    status: str = Status.NEW.value
    payment: str = "default"

    def from_form(self, form):

        self.cart = json.loads(form["cart"])
        delivery = True if form["delivery"] == "true" else False
        self.delivery = delivery

        self.client_name = form["name"]
        self.client_phone = form["phone"]
        self.client_comment = form["comment"]
        self.client_email = form["email"]

        if delivery:
            self.street = form["street"]
            self.house = form["house"]
            self.flat = form["flat"]
            self.porch = form["porch"]

        self.total = int(form["total"])

        self.date = form["date"] + ", " + form["time"]
        self.payment = form["payment"]

        return self

    def save(self):
        if document_by_id(order_collection, self.id):
            order_collection.replace_one({"_id": self.id}, self.dict(by_alias=True))
        else:
            self.id = new_document_id(order_collection)
            self.sentAt = datetime.now().strftime("%m/%d/%Y, %H:%M")
            order_collection.insert_one(self.dict(by_alias=True))

    def delete(self):
        order_collection.delete_one({"_id": self.id})
