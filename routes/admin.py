import datetime

from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    flash,
    url_for,
    jsonify,
)
from flask_login import (
    login_required,
    current_user,
    LoginManager,
    login_user,
    logout_user,
)

from werkzeug.security import check_password_hash
import re

from models.database import admin_by_username, document_by_codename
from models.dish import (
    Dish,
    DishCategory,
    CategoryType,
    dish_category_type_collection,
    dish_category_collection,
    ENCategoryType,
    dish_collection,
)
from models.admin import Admin, admin_collection
from models.order import Order, Status, order_collection
from models.reservation import Reservation, reservation_collection
from models.settings import Settings, settings_collection
from models.slider import Slider, slider_collection
from models.announce import Announce, announce_collection, document_by_id


login_manager = LoginManager()
login_manager.login_view = "admin.login"

admin_router = Blueprint("admin", __name__)


@admin_router.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/admin")

    if request.method == "POST":
        check_admin = admin_by_username(admin_collection, request.form["username"])
        if check_admin:
            if check_password_hash(check_admin["password"], request.form["password"]):
                check_admin = Admin(**check_admin)
                login_user(check_admin)
                return redirect(url_for("admin.admin_main"))
            else:
                flash("Password is invalid!")
                return redirect(url_for("admin.login"))
        else:
            flash("Undefined Login")
            return redirect(url_for("admin.login"))
    else:
        return render_template("admin/login.html")


@admin_router.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(userid):
    admin = document_by_id(admin_collection, int(userid))
    if admin is None:
        return redirect(url_for("admin.login"))
    return Admin(**admin)


@admin_router.route("/", methods=["GET", "POST"])
@login_required
def admin_main():
    return redirect(url_for("admin.dish_categories"))


@admin_router.route("/dishes", methods=["GET", "POST"])
@login_required
def dish_categories():
    if request.method == "POST":
        print("CALL1")

        form = request.form.to_dict()

        form["code_name"] = re.sub(" +", " ", form["code_name"])
        form["code_name"] = form["code_name"].strip()
        form["code_name"] = form["code_name"].replace(" ", "_")

        form["isShow"] = True if form["isShow"] == "on" else False
        DishCategory().from_form(form).save()

        return redirect(url_for("admin.dish_categories"))

    else:
        print("CALL2")

        data = [
            DishCategory(**category).to_dict
            for category in dish_category_collection.find()
        ]

        types = list(dish_category_type_collection.find())

        # types = ["Restaraunt", "Banquet", "Souvenirs", "Food", "VineCard", "Drinks"]

        return render_template(
            "admin/dishes/dishCategories.html", data=data, types=types
        )


@admin_router.route("/dishes/create", methods=["GET", "POST"])
@login_required
def create_dish():
    if request.method == "POST":
        form = request.form.to_dict()

        form["code_name"] = re.sub(" +", " ", form["code_name"])
        form["code_name"] = form["code_name"].strip()
        form["code_name"] = form["code_name"].replace(" ", "_")

        form["isShow"] = True if form["isShow"] == "on" else False

        Dish().from_form(form, request.files.get("image")).save()

        return redirect(
            url_for(
                "admin.dishes",
                category_code=dish_category_collection.find_one(
                    {"_id": int(form["category"])}
                )["code_name"],
            )
        )

    else:
        return render_template(
            "admin/dishes/addDish.html",
            data=list(dish_category_collection.find()),
            types=list(dish_category_type_collection.find()),
        )


@admin_router.route("/dishes/<category_code>", methods=["GET", "POST"])
@login_required
def dishes(category_code):
    dish_category = document_by_codename(dish_category_collection, category_code)
    if dish_category is None:
        return redirect(url_for("admin.dish_categories"))
    dish_category = DishCategory(**dish_category)

    if request.method == "POST":
        if request.form["_method"] == "PUT":

            form = request.form.to_dict()
            form["isShow"] = True if form["isShow"] == "on" else False
            dish_category.from_form(form).save()

            return redirect(url_for("admin.dish_categories"))

        elif request.form["_method"] == "DELETE":
            dish_category.delete()
            return redirect(url_for("admin.dish_categories"))
    else:
        return render_template(
            "admin/dishes/dishes.html",
            data=list(
                dish_collection.find(
                    {"category": dish_category.id},
                    {
                        "category": False,
                        "image": False,
                        "language.en": False,
                        "language.uk.description": False,
                    },
                )
            ),
            types=list(dish_category_type_collection.find()),
        )


@admin_router.route("/dishes/<category_code>/<dish_code>", methods=["GET", "POST"])
@login_required
def dish(category_code, dish_code):
    dish = document_by_codename(dish_collection, dish_code)
    if dish is None:
        return redirect(url_for("admin.dish_categories"))
    dish = Dish(**dish)

    if request.method == "POST":
        if request.form["_method"] == "PUT":
            form = request.form.to_dict()
            form["isShow"] = True if form["isShow"] == "on" else False

            dish.from_form(form, request.files.get("image")).save()

        elif request.form["_method"] == "DELETE":
            dish.delete()

        return redirect(url_for("admin.dishes", category_code=category_code))
    else:
        return render_template(
            "admin/dishes/editDish.html",
            data=dish.dict(),
            data_categories=list(dish_category_collection.find()),
        )


@admin_router.route("/orders", methods=["GET", "POST"])
@login_required
def orders():
    if request.method == "POST":
        pass
    else:
        return render_template(
            "admin/orders/orders.html",
            data=list(
                order_collection.find(
                    {},
                    {
                        "cart": False,
                        "client_email": False,
                        "client_comment": False,
                        "street": False,
                        "house": False,
                        "flat": False,
                        "porch": False,
                        "sentAt": False,
                    },
                )
            ),
        )


@admin_router.route("/orders/<int:orderID>", methods=["GET", "POST"])
@login_required
def order(orderID):
    order = document_by_id(order_collection, orderID)
    if order is None:
        return redirect(url_for("admin.orders"))
    order = Order(**order)

    if request.method == "POST":
        if request.form["_method"] == "DELETE":
            order.delete()
        else:
            form = request.form.to_dict()
            order.status = form["status"]
            order.save()

        return redirect(url_for("admin.orders"))
    else:
        return render_template(
            "admin/orders/infoOrder.html",
            data=order.dict(),
            data_statuses=Status.list(),
            dishes=list(dish_collection.find()),
        )


@admin_router.route("/reservations", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def reservations():
    return render_template(
        "admin/reservations/reservations.html",
        data=list(reservation_collection.find()),
    )


@admin_router.route(
    "/reservations/<int:reservationID>", methods=["GET", "POST", "PUT", "DELETE"]
)
@login_required
def reservation(reservationID):
    reserve = document_by_id(reservation_collection, reservationID)
    if reserve is None:
        return redirect(url_for("admin.reservations"))
    reserve = Reservation(**reserve)

    if request.method == "POST":
        if request.form["_method"] == "DELETE":
            reserve.delete()
        else:
            form = request.form.to_dict()
            reserve.isAccepted = True if form["isAccepted"] == "on" else False
            reserve.save()

        return redirect(url_for("admin.reservations"))
    else:
        return render_template(
            "admin/reservations/infoReservation.html", data=reserve.dict()
        )


@admin_router.route("/sliders/create", methods=["GET", "POST"])
@login_required
def create_slider():
    if request.method == "POST":
        form = request.form.to_dict()
        form["isShow"] = True if form["isShow"] == "on" else False
        Slider().from_form(form, request.files.get("image")).save()

        return redirect(url_for("admin.sliders"))
    else:
        return render_template("admin/sliders/addSlider.html")


@admin_router.route("/sliders", methods=["GET"])
@login_required
def sliders():
    if request.method == "GET":
        return render_template(
            "admin/sliders/sliders.html",
            data=list(slider_collection.find({}, {"image": False})),
        )


@admin_router.route("/sliders/<int:sliderID>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def slider(sliderID):
    slider = document_by_id(slider_collection, sliderID)
    if slider is None:
        return redirect(url_for("admin.sliders"))
    slider = Slider(**slider)

    if request.method == "POST":
        if request.form["_method"] == "PUT":
            form = request.form.to_dict()
            form["isShow"] = True if form["isShow"] == "on" else False
            slider.from_form(form, request.files.get("image")).save()

        elif request.form["_method"] == "DELETE":
            slider.delete()

        return redirect(url_for("admin.sliders"))
    else:
        return render_template("admin/sliders/editSlider.html", data=slider.dict())


@admin_router.route("/announce/create", methods=["GET", "POST"])
@login_required
def create_announce():
    if request.method == "POST":
        form = request.form.to_dict()
        form["isShow"] = True if form["isShow"] == "on" else False

        Announce().from_form(form, request.files.get("image")).save()

        return redirect(url_for("admin.announces"))
    else:
        return render_template("admin/announce/addPost.html")


@admin_router.route("/announces", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def announces():
    if request.method == "GET":
        return render_template(
            "admin/announce/posts.html",
            data=list(announce_collection.find()),
        )


@admin_router.route("/announces/<int:postID>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def announce_post(postID):
    announce = document_by_id(announce_collection, postID)
    if announce is None:
        return redirect(url_for("admin.announces"))
    announce = Announce(**announce)

    if request.method == "POST":
        if request.form["_method"] == "PUT":
            form = request.form.to_dict()
            form["isShow"] = True if form["isShow"] == "on" else False

            announce.from_form(form, request.files.get("image")).save()

        elif request.form["_method"] == "DELETE":
            announce.delete()

        return redirect(url_for("admin.announces"))
    else:
        return render_template("admin/announce/editPost.html", data=announce.dict())


@admin_router.route("/admins", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def admins():
    if request.method == "GET":
        return render_template(
            "admin/admins/admins.html",
            data=list(admin_collection.find({}, {"password": False})),
        )


@admin_router.route("/admins/create", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def create_admin():
    if request.method == "POST":
        form = request.form.to_dict()
        Admin().from_form(form).save()

        return redirect(url_for("admin.admins"))
    else:
        return render_template("admin/admins/addAdmin.html")


@admin_router.route("/admins/<username>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def admin(username):
    admin = admin_by_username(admin_collection, username)
    if admin is None:
        return redirect(url_for("admin.admins"))
    admin = Admin(**admin)

    if request.method == "POST":
        if request.form["_method"] == "PUT":
            form = request.form.to_dict()
            admin.from_form(form).save()

        elif request.form["_method"] == "DELETE":
            admin.delete()

        return redirect(url_for("admin.admins"))
    else:
        return render_template(
            "admin/admins/editAdmin.html", data=admin.dict(exclude={"password"})
        )


@admin_router.route("/settings", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def settings():
    settings = Settings(**document_by_id(settings_collection, 1))

    if request.method == "POST":
        form = request.form.to_dict()
        settings.from_form(form).save()

    return render_template("admin/settings.html", data=settings.dict())
