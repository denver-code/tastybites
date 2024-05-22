import ssl
import sass
from flask import Flask, request, g, session, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

from os.path import join, dirname, realpath
from flask_babel import Babel

from routes.website import website_router
from routes.admin import admin_router, login_manager
from routes.errors import page_not_found, internal_server_error

from models.settings import Settings
from models.admin import Admin

# from models.dish import (
#     CategoryType,
#     UKCategoryType,
#     ENCategoryType,
#     DishCategory,
#     dish_category_type_collection,
# )

# types = ["Restaraunt", "Banquet", "Souvenirs", "Food", "VineCard", "Drinks"]

# for i, type in enumerate(types):
#     category_type = CategoryType(en_type=type, uk_type=type, _id=i)
#     dish_category_type_collection.insert_one(category_type.dict())

# for category in ENCategoryType:
#     cat_t = CategoryType(en_type=category.value, uk_type="None")
# Settings().save()
# Admin().save()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.register_blueprint(admin_router, url_prefix="/admin")
app.register_blueprint(website_router)
app.config["BABEL_DEFAULT_LOCALE"] = "uk"
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)
app.config["MONGODB_SETTINGS"] = {
    "host": os.getenv("DATABASE"),
    "ssl_cert_reqs": ssl.CERT_NONE,
}


@app.route("/robots.txt")
@app.route("/sitemap.xml")
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


directory = "objects"
upload_folder = join(join(dirname(realpath(__file__)), "static/"))
folder = join(upload_folder, directory)
os.makedirs(folder, exist_ok=True)

UPLOAD_FOLDER = join(dirname(realpath(__file__)), "static/objects/")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config.update(SECRET_KEY="MariaGarden_Secret_Key_RDDR")

login_manager.init_app(app)

sass.compile(dirname=("static/sass", "static/css"), output_style="compressed")

babel = Babel(app, default_locale="uk")


@babel.localeselector
def get_locale():
    if "lang" in session:
        return session["lang"]
    lang = request.accept_languages.best_match(["en", "uk", "ru"])
    if not lang:
        lang = "uk"
    return lang if "ru" not in lang else "uk"


@app.before_request
def before_request():
    g.locale = str(get_locale())


extra_dirs = ["static/sass", "static/js"]
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
