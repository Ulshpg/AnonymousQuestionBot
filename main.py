from buttons import *
from config import *
import html
from database import insert_data, get_data, get_all_vips, add_vip, get_username_by_id
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token=TELEGRAM_TOKEN) # Токен
dp = Dispatcher(bot, storage=MemoryStorage())
yoomoney_client = Client(YOOMONEY_TOKEN)


class VIP:
    users = list()


    async def update_vip_users():
        VIP.users = await get_all_vips()

    async def add_vip_user(id):
        VIP.users = await add_vip(id)

class User(StatesGroup):
    write = State()
    answer = State()

class Payment(StatesGroup):
    pay = State()
    check = State()


async def check_payment(label):
    history = yoomoney_client.operation_history()
    print(f"\nLabel: {label}")
    for operation in history.operations:
        if operation.label == label and operation.status == "success":
            print(f"ПЛАТЁЖ {operation.amount} УСПЕШНО ПРОШЁЛ")
            return True
            break
    else:
        print("ПЛАТЁЖ НЕ ОБНАРУЖЕН")
        return False

async def get_username(tmp_username):
    if "none" == str(tmp_username).lower():
        username = "Отсутствует"
    else:
        username = f"@{tmp_username}"
    return username

async def on_startup(_):
    print("Бот онлайн")
    await VIP.update_vip_users()

@dp.message_handler(commands="start", state='*')
async def commands_start(message, state=FSMContext):
    user_id = message.from_user.id
    name_user = message.from_user.first_name
    username = await get_username(message.from_user.username)
    await insert_data(user_id, name_user, username)
    if len(message.text.split()) > 1: # реферальная система
        unique_code = message.text.split()[1]
        if unique_code.isdigit():
            unique_code = int(unique_code)
        if unique_code == user_id:
            await message.answer("Вы не можете написать сами себе!", reply_markup=removeButton)
            await state.finish()
        else:
            await message.answer("💬Сейчас ты можешь написать сообщение тому человеку, \
                                 который опубликовал эту ссылку\n\n✍🏻 Напиши своё сообщение:", reply_markup=cancelMenu)
            await User.write.set()
            async with state.proxy() as data:
                data['other_id'] = unique_code
    else:
        await message.answer(f"🔗 Вот твоя личная ссылка:\n\n{LINK}?start={message.from_user.id}\n\nОпубликуй её и получай анонимные сообщения", 
                             reply_markup=removeButton, 
                             disable_web_page_preview=True)

@dp.message_handler(commands="support", state='*')
async def commands_support(message, state=FSMContext):
    await message.answer("<i>Если у Вас появились вопросы по работе бота, то можете написать сюда -</i> @AnQSupport", parse_mode="HTML")
    await state.finish()

@dp.message_handler(Text("Отмена ❌"), state=User.write)
async def user_write_cancel(message: types.Message, state):
    await message.answer("Вы отменили отправку сообщения!", reply_markup=removeButton)
    await state.finish()

@dp.message_handler(state=User.write)
async def user_write(message: types.Message, state: FSMContext):
    text = html.escape(message.text)
    if len(text) < 4000:
        async with state.proxy() as data:
            other_id = data['other_id']
            user_id = message.from_user.id
            name_user = message.from_user.first_name
            username = await get_username(message.from_user.username)
            await insert_data(user_id, name_user, username)
            try:
                await bot.send_message(other_id, f"📨 <b>Получено новое сообщение</b>\n\n{text}", parse_mode="HTML", reply_markup = await GetResultMenu(user_id))
                print(f"\n{username}({user_id}) -> {await get_username_by_id(other_id)}({other_id})\nСообщение: {text}\n")

                await message.answer(f"<b>Ваше сообщение отправлено!</b>\n\n🔗 Вот твоя личная ссылка:\n\n\
{LINK}?start={message.from_user.id}\n\n\
Опубликуй её и получай анонимные сообщения", parse_mode="HTML", reply_markup=removeButton, disable_web_page_preview=True)
                
            except Exception as e:
                await message.answer("<i>Сообщение не было отправлено</i>", parse_mode="HTML")
                print(f"\nОшибка: {e}")
            await state.finish()
    else:
        await message.answer("<i>Вы не можете отправить слишком длинное сообщение! Сократите его объём.</i>", parse_mode="HTML")

@dp.callback_query_handler(lambda c: "HU" in c.data, state="*")
async def WhoIsIt(call, state):
    user_id = call.from_user.id
    if user_id in VIP.users:
        await call.answer("Человек")
        name, username = await get_data(int(call.data[2:]))
        name = html.escape(name)
        username = html.escape(username)
        await bot.send_message(user_id, f"<b>Данные о человеке, который отправил сообщение выше:</b>\n\n<b>Имя -</b> {name}\n<b>Юзернейм -</b> {username}", parse_mode="HTML")
    else:
        await call.answer("Покупка VIP")
        await bot.send_message(user_id, "<b>Хочешь узнать, кто так думает и пишет?</b>\nЕсли хочешь видеть имена отправителей, то можно приобрести <b>VIP</b>👑\n\n<b>Цена:</b> <s>99 рублей</s> <b>59 рублей</b> (-40%)\n<b>Срок: НАВСЕГДА</b>", 
                               parse_mode="HTML", 
                               reply_markup = await GetPaymentsMenu(user_id))

@dp.callback_query_handler(lambda c: "check" == c.data, state="*")
async def CheckPayment(call, state):
    user_id = call.from_user.id
    if user_id not in VIP.users:
        label = str(user_id)
        if await check_payment(label):
            await VIP.add_vip_user(user_id)
            await call.answer("Оплата прошла успешно")
            await bot.edit_message_text("<b>Вы приобрели VIP-статус👑</b>\n\n<b>Теперь Вы видите информацию о пользователе, который вам написал!</b>", 
                                        chat_id=user_id, 
                                        message_id=call.message.message_id, 
                                        parse_mode="HTML")
            print(f"{user_id} добавлен VIP\n")
        else:
            await call.answer("Оплата не получена")
    else:
        await call.answer("Вы уже VIP")

@dp.message_handler(Text("Отмена ❌"), state=User.answer)
async def user_write_cancel(message: types.Message, state):
    await message.answer("Вы отменили отправку ответа!", reply_markup=removeButton)
    await state.finish()

@dp.callback_query_handler(lambda c: "AN" in c.data, state="*")
async def answer(call, state):
    user_id = call.from_user.id
    await call.answer("Ответ пользователю")
    await bot.send_message(user_id, "<b>Отправьте ваш ответ на анонимное сообщение</b>", reply_markup=cancelMenu, parse_mode="HTML")
    await User.answer.set()
    async with state.proxy() as data:
        data['other_id'] = call.data[2:]

@dp.message_handler(state=User.answer)
async def user_answer(message: types.Message, state: FSMContext):
    text = html.escape(message.text)
    if len(text) < 4000:
        async with state.proxy() as data:
            other_id = int(data['other_id'])
            user_id = message.from_user.id
            name_user = message.from_user.first_name
            username = await get_username(message.from_user.username)
            await bot.send_message(other_id, f"<b>На ваше сообщение ответили:</b>\n\n{text}", parse_mode="HTML")
            print(f"\n{username}({user_id}) -> {await get_username_by_id(other_id)}({other_id})\nОтвет: {text}\n")
            await message.answer(f"<b>Ваш ответ был отправлен!</b>\n\n🔗 Вот твоя личная ссылка:\n\n{LINK}?start={message.from_user.id}\n\nОпубликуй её и получай анонимные сообщения", 
                                 parse_mode="HTML", 
                                 reply_markup=removeButton, 
                                 disable_web_page_preview=True)
            await insert_data(user_id, name_user, username)
            await state.finish()
    else:
        await message.answer("<i>Вы не можете отправить слишком длинное сообщение! Сократите его объём.</i>", parse_mode="HTML")


# админка #
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID, commands="add_vip", state="*")
async def add_new_vip_users(message: types.Message, state: FSMContext):
    text = message.text
    if len(text.split(" ")) == 2:
        _, user_id = text.split(" ")
        if user_id.isdigit():
            try:
                await VIP.add_vip_user(int(user_id))
                await message.answer("пользователь добавлен")
            except:
                await message.answer("Неизвестная ошибка")
        else:
            await message.answer("ID должен быть числом")
    else:
        await message.answer("Неправильное количество атрибутов")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)