import requests
from pymongo import MongoClient
import ast
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("DATABASE"))

db = client["HataBagata"]
dishesc = db["dish"]

API_TOKEN = ""


def send_message(message):
    url_req = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id=-1001600637560&text={message}&parse_mode=html"
    f = requests.get(url_req)


def new_reservation(reservation):
    if "#" in reservation["comment"]:
        reservation["comment"] = reservation["comment"].replace("#", "")
    if "+" in reservation["phone"]:
        reservation["phone"] = reservation["phone"].replace("+", "")
    msg = f"""<b>У вас нова резервація!</b>

<b>Ім'я клієнта:</b> <i>{reservation['name']}</i>
<b>Телефон клієнта:</b> <a href="tel:%2B{"".join(reservation['phone'].split())}">%2B{"".join(reservation['phone'].split())}</a>
<b>Коментар:</b> <i>{reservation['comment']}</i>
<b>Кількість людей:</b> <i>{reservation['persons']}</i>
<b>Дата:</b> <i>{reservation['date']} о {reservation['time']}</i>"""
    send_message(msg)


def new_order(order):
    order["cart"] = ast.literal_eval(order["cart"])
    dishes = []
    if "#" in order["comment"]:
        order["comment"] = order["comment"].replace("#", "")
    if "+" in order["phone"]:
        order["phone"] = order["phone"].replace("+", "")
    for i in order["cart"]:
        dishes.append([int(i), int(order["cart"][i])])
    formatter_str = ""
    for i in dishes:
        dish_obj = dishesc.find_one({"_id": i[0]})
        formatter_str = (
            formatter_str + f"- {dish_obj['language']['uk']['name']} - {i[1]}шт.\n"
        )
    msg = f"""
<b>У вас нове замовлення!</b>

<b>Ім'я клієнта:</b> <i>{order['name']}</i>
<b>Пошта клієнта:</b> <i>{order['email']}</i>
<b>Телефон клієнта:</b> <a href="tel:%2B{"".join(order['phone'].split())}">%2B{"".join(order['phone'].split())}</a>
<b>Коментар:</b> <i>{order['comment']}</i>
<b>Блюда:</b>
<i>{formatter_str}</i>
"""
    if order["delivery"] == "true":
        msg += f"""<b>Вулиця:</b> <i>{order['street']}</i>
<b>Дім:</b> <i>{order['house']}</i>
<b>Під'їзд:</b> <i>{order['porch']}</i>
<b>Квартира:</b> <i>{order['flat']}</i>
"""

    if order["delivery"] == "true":
        price = "50" if order["detail_delivery"] == "porch" else "55"
        msg += f"""
<b>Всього:</b> <i>{order['total']} GBP + {price} GBP доставка</i>
"""
    else:
        msg += f"""
<b>Всього:</b> <i>{order['total']} GBP</i>
"""

    msg += f"""<b>Дата замовлення:</b> <i>{order['date']} о {order['time']}</i>"""
    send_message(msg)
