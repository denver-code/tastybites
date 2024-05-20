import os
import shutil
from PIL import Image
from flask import current_app
from dotenv import load_dotenv

load_dotenv()

from werkzeug.utils import secure_filename
import pymongo
from pymongo.collection import Collection

client = pymongo.MongoClient(os.getenv("DATABASE"))
database = client["HataBagata"]


def new_document_id(collection: Collection):
    if collection.find().count() == 0:
        return 1
    return collection.find().limit(1).sort([("$natural", -1)])[0]["_id"] + 1


def document_by_id(collection: Collection, id: int):
    return collection.find_one({"_id": id})


def document_by_codename(collection: Collection, code_name: str):
    return collection.find_one({"code_name": code_name})


def admin_by_username(collection: Collection, username: str):
    return collection.find_one({"username": username})


def save_image(image, directory, id):
    filename, file_extension = os.path.splitext(image.filename)
    filename = f"image{file_extension}"
    filename = secure_filename(filename)

    upload_folder = os.path.join(current_app.config["UPLOAD_FOLDER"])
    folder = os.path.join(upload_folder, directory)
    os.makedirs(folder, exist_ok=True)

    image_folder = os.path.join(folder, str(id))
    os.makedirs(image_folder, exist_ok=True)

    image = Image.open(image)
    image.save(os.path.join(image_folder, filename), optimize=True)

    return f"objects/{directory}/{id}/{filename}"


def delete_image(directory: str, id: int):
    upload_folder = os.path.join(current_app.config["UPLOAD_FOLDER"])
    folder = os.path.join(upload_folder, directory)
    image_folder = os.path.join(folder, str(id))
    try:
        shutil.rmtree(image_folder)
    except Exception as e:
        print(e)
