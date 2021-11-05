from telegram import ReplyKeyboardMarkup, \
    InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from .models import *

addorder = "Buyurtma berish"
savatcha = "Savatcha"
orderhistory = "Buyurtmalar tarixi"
hisobkitob = "Hisob kitob"
info = "Info"


def main_button():
    button = [
        [addorder],
        [savatcha, orderhistory],
        [hisobkitob, info]
    ]
    return ReplyKeyboardMarkup(button, resize_keyboard=True)


def phone_button():
    contact = KeyboardButton(text="Raqam yuborish", request_contact=True)
    button = [
        [contact]
    ]
    return ReplyKeyboardMarkup(button, resize_keyboard=True)


def product_all_button(page):
    button = []
    res = []
    products = Product.objects.filter(quantity__gte=1)
    if len(products) > page * 10:
        products = Product.objects.filter(quantity__gte=1)[(page - 1) * 10: page * 10:]
    else:
        products = Product.objects.all()[(page - 1) * 10:]

    sanoq = 1
    for i in products:
        res.append(InlineKeyboardButton(f"{i.name}", callback_data=f"product_{i.id}"))
        if len(res) == 2:
            button.append(res)
            res = []
        sanoq += 1
    if len(res) != 0:
        button.append(res)
        res = []
    res.append(InlineKeyboardButton("⏩⏩", callback_data="next"))
    res.append(InlineKeyboardButton("❌", callback_data="cancel"))
    res.append(InlineKeyboardButton("⏪⏪", callback_data="back"))
    button.append(res)
    return InlineKeyboardMarkup(button)


def order_button(id):
    button = []

    button.append([InlineKeyboardButton("Buyurtma berish", callback_data=f'order_{id}')])
    button.append([InlineKeyboardButton("Savatchaga qo'shish", callback_data=f'savat_{id}')])
    button.append([InlineKeyboardButton("Bekor qilish", callback_data=f'cancel')])

    return InlineKeyboardMarkup(button)


def count_button(id):
    button = []
    res = []
    res.append(InlineKeyboardButton("⬆️", callback_data='up'))
    res.append(InlineKeyboardButton("⬇️", callback_data='down'))
    button.append(res)
    button.append([InlineKeyboardButton("✅ Tasdiqlash", callback_data=f'confirm_{id}')])
    return InlineKeyboardMarkup(button)


def savatcha_button(savatcha):
    res = []
    button = []
    for i in savatcha:
        res.append(InlineKeyboardButton("➖", callback_data=f'minus_{i.id}'))
        res.append(InlineKeyboardButton(f"{i.product.name}", callback_data=f"{i.product.name}_1"))
        res.append(InlineKeyboardButton("➕", callback_data=f"plus_{i.id}"))
        res.append(InlineKeyboardButton("❌", callback_data=f'delete_{i.id}'))
        button.append(res)
        res = []
    button.append([InlineKeyboardButton("✅Tasqidlash", callback_data="confirm")])
    button.append([InlineKeyboardButton("❌Bekor qilish", callback_data="cancel")])
    return InlineKeyboardMarkup(button)

def muddat_button():
    button = []
    button.append([InlineKeyboardButton('Kunlik', callback_data="day"),
                   InlineKeyboardButton('Haftalik', callback_data="week")])
    button.append([InlineKeyboardButton('Oylik', callback_data="month"),
                   InlineKeyboardButton('Yillik', callback_data="year")])
    button.append([InlineKeyboardButton("Ortga", callback_data='cancel')])
    return InlineKeyboardMarkup(button)


def director_main_button():
    button = [
        ["➕ Add product"],
        ["➕Add admin"]
    ]
    return ReplyKeyboardMarkup(button)


