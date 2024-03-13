from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from yoomoney import Client, Quickpay
from config import PRICE


cancelMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отмена ❌'))
removeButton = ReplyKeyboardRemove()


async def GetResultMenu(user_id):
    ResultMenu = InlineKeyboardMarkup(1).add(
        InlineKeyboardButton('📩 Ответить', callback_data=f"AN{user_id}"),
        InlineKeyboardButton('👁️ Кто это?', callback_data=f"HU{user_id}"))
    return ResultMenu
    

async def GetPaymentsMenu(user_id):
    data_for_check = "check"
    label = user_id
    quickpay = Quickpay(
            receiver="4100118271372368",
            quickpay_form="shop",
            targets="Sponsor this project",
            paymentType="SB",
            sum=PRICE,
            label=label
            )
    PaymentsMenu = InlineKeyboardMarkup(1).add(
        InlineKeyboardButton('Оплатить', url=quickpay.redirected_url),
        InlineKeyboardButton('Проверить оплату', callback_data=data_for_check))
    return PaymentsMenu