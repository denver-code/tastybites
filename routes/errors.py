from flask import render_template

from models.database import document_by_id
from models.dish import Dish, dish_collection
from models.settings import Settings, settings_collection


def page_not_found(e):
    return (
        render_template(
            "errors/404.html",
            info=document_by_id(settings_collection, 1),
            dishes=list(dish_collection.find({'isShow': True}))
        ),
        404,
    )


def internal_server_error(e):
    return (
        render_template(
            "errors/500.html",
            info=document_by_id(settings_collection, 1),
            dishes=list(dish_collection.find({'isShow': True}))
        ),
        500,
    )
