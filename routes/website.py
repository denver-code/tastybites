from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    flash,
    url_for,
    g,
    session,
)
from flask_cors import cross_origin
import ast

from models.database import document_by_id
from models.dish import Dish, DishCategory, CategoryType, dish_collection, dish_category_type_collection, \
    dish_category_collection
from models.order import Order, order_collection
from models.reservation import Reservation
from models.settings import Settings, settings_collection
from models.slider import Slider, slider_collection
from models.announce import Announce, announce_collection
from routes.errors import page_not_found
from api.bot import (
    new_reservation,
    new_order
)

website_router = Blueprint("website", __name__)


@website_router.route("/change_lang", methods=["GET", "POST"])
def change_lang():
    if request.method == "POST":
        session["lang"] = request.form["lang"]
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@website_router.route("/", methods=["GET"])
def index():
    return render_template(
        "website/index.html",
        categories=list(dish_category_collection.find({'isShow': True})),
        slider=list(slider_collection.find({'isShow': True})),
        info=document_by_id(settings_collection, 1),
        dishes=list(dish_collection.find({'isShow': True}))
    )


@website_router.route("/announces", methods=["GET"])
def announces():
    return render_template(
        "website/announce.html",
        categories=list(dish_category_collection.find({'isShow': True})),
        announce=list(announce_collection.find({'isShow': True})),
        info=document_by_id(settings_collection, 1),
        dishes=list(dish_collection.find({'isShow': True}))
    )


@website_router.route("/delivery", methods=["GET"])
def delivery():
    return render_template(
        "website/delivery.html",
        info=document_by_id(settings_collection, 1),
        categories=list(dish_category_collection.find({'isShow': True})),
        types=list(dish_category_type_collection.find()),
        dishes=list(dish_collection.find({'isShow': True}))
    )


@website_router.route("/menu", methods=["GET"])
def menu():
    return render_template(
        "website/menu.html",
        info=document_by_id(settings_collection, 1),
        categories=list(dish_category_collection.find({'isShow': True})),
        types=list(dish_category_type_collection.find()),
        dishes=list(dish_collection.find({'isShow': True}))
    )


@website_router.route("/reserve", methods=["POST"])
@cross_origin()
def reserve():
    form = request.form.to_dict()
    new_reservation(form)
    Reservation().from_form(form).save()

    return redirect(request.referrer)


@website_router.route("/order", methods=["POST"])
@cross_origin()
def order():
    form = request.form.to_dict()

    _order = Order().from_form(form)
    _order.save()

    new_order(request.form.to_dict())

    return redirect(
        url_for(
            "website.order_id",
            order_id=_order.id)
    )


@website_router.route("/order/<order_id>", methods=["GET"])
@cross_origin()
def order_id(order_id):
    order = document_by_id(order_collection, int(order_id))
    keys_to_delete = ["client_email", "client_name", "client_phone"]
    for key in keys_to_delete:
        del order[key]
    if order:
        return render_template(
            "website/order.html",
            info=document_by_id(settings_collection, 1),
            order=order,
            categories=list(dish_category_collection.find()),
            types=list(dish_category_type_collection.find()),
            dishes=list(dish_collection.find())
        )

    return redirect(request.referrer)


@website_router.route("/holl/<code_name>", methods=["GET"])
def holl(code_name):
    try:
        return render_template(
            "website/holl.html",
            info=document_by_id(settings_collection, 1),
            categories=list(dish_category_collection.find({'isShow': True})),
            types=list(dish_category_type_collection.find()),
            dishes=list(dish_collection.find({'isShow': True})),
            target_holl=code_name
        )
    except:
        return page_not_found("e")


@website_router.route("/shop", methods=["GET"])
def shop():
    return render_template(
        "website/shop.html",
        info=document_by_id(settings_collection, 1),
        categories=list(dish_category_collection.find({'isShow': True})),
        types=list(dish_category_type_collection.find()),
        dishes=list(dish_collection.find({'isShow': True})),
    )


@website_router.route("/contacts", methods=["GET"])
def contacts():
    return render_template(
        "website/contacts.html",
        info=document_by_id(settings_collection, 1),
        dishes=list(dish_collection.find({'isShow': True})),
        categories=list(dish_category_collection.find({'isShow': True})),
    )

# @website_router.route("/alt_menu", methods=["GET"])
# def alt_menu():
#     return render_template(
#         "website/alt_menu.html",
#         info=document_by_id(settings_collection, 1),
#         dishes=list(dish_collection.find({'isShow': True}))
#     )
