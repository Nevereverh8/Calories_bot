import asyncio
import datetime as dt
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from tg_bot.tg_keyboards import refresh_keyb, start_keyb
import database.db as db

cmd_router = Router()
cb_router = Router()
msg_router = Router()
help_text = '\nI use folowing designations:\ncal - calories\ng - grams\ncal/100g - calories per 100 grams of product\np - proteins\nf - fats\nch - carbohydrates\n\nPlease, use one of the folowing formats to send data:\n\n1) cal/100g*g p f ch\n(cal, p, f, ch will be multiplied by g)\n\n2)cal p f ch \n(nothing will be multiplied)\n\n\n any data but cal or cal/100g is optional, if you want to track specific p,f or ch fill other ones with zeroes (order matters p->f->ch'


wrong_format_text = 'Wrong format, please use one of examples:\ncalories*grams proteins fats carbohyrates\nor\ncalories proteins fats carbohydrates\n\n if grams specified, everything else will be multiplied by grams/100'


# Command handlers
@cmd_router.message(CommandStart())
async def cmd_start(message: Message):
    print(message.chat.id)
    await db.add_user(message.chat.id)
    await message.delete()
    await message.answer("Hi, I'll help you to track all your nutrition data everyday"+help_text, reply_markup=start_keyb)


@cmd_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.delete()
    await message.answer(help_text, reply_markup=start_keyb)


@msg_router.message(F.text[0] != '/')
async def record(message: Message):
    text = message.text
    if text[0] == '-':
        text = text[1:]
        multiplier = -1
    else:
        multiplier = 1
    # with * or x
    for s in [' x ', ' х ', ' * ',
              ' x', ' х', ' *',
              'x ', 'х ', '* ',
              'x', 'х', '*']:
        if s in text:
            print(text.split(s))
            if all(i.strip().isdigit() for i in text.split(s)[1].split(' ')) and text.split(s)[0].isdigit():
                calories = int(text.split(s)[0].strip())
                if len(text.split(s)[1].split(' ')) >= 1:
                    multiplier *= int(text.split(s)[1].split(' ')[0])/100
                    calories = int(multiplier * calories)
                else:
                    await message.answer(wrong_format_text)
                if len(text.split(s)[1].split(' ')) >= 2:
                    proteins = int(int(text.split(s)[1].split(' ')[1]) * multiplier)
                else:
                    proteins = 0
                if len(text.split(s)[1].split(' ')) >= 3:
                    fats = int(int(text.split(s)[1].split(' ')[2]) * multiplier)
                else:
                    fats = 0
                if len(text.split(s)[1].split(' ')) >= 4:
                    carbohydrates = int(int(text.split(s)[1].split(' ')[3]) * multiplier)
                else:
                    carbohydrates = 0
                print(multiplier, calories, proteins, fats, carbohydrates)
                await db.add_record(message.chat.id, calories, proteins, fats, carbohydrates)
                await message.delete()
                break
            else:
                await message.answer(wrong_format_text)
                break
    # without * or x
    else:
        if all([i.strip().isdigit() for i in text.split(' ')]):
            calories = int(text.split(' ')[0]) * multiplier
            if len(text.split(' ')) >= 2:
                proteins = int(text.split(' ')[1]) * multiplier
            else:
                proteins = 0
            if len(text.split(' ')) >= 3:
                fats = int(text.split(' ')[2]) * multiplier
            else:
                fats = 0
            if len(text.split(' ')) >= 4:
                carbohydrates = int(text.split(' ')[3]) * multiplier
            else:
                carbohydrates = 0
            await db.add_record(message.chat.id, calories, proteins, fats, carbohydrates)
            await message.delete()
        else:
            await message.answer(wrong_format_text)


@cb_router.callback_query(F.data == 'refresh')
async def refresh(callback: CallbackQuery):
    await callback.answer('Data in message refreshed')
    records_list = await db.get_today_records(callback.message.chat.id)
    if records_list:
        text = f'Last refreshed: {dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
        text += 'cal / p / f / ch\n'
        t_cal, t_prot, t_fats, t_carb = 0, 0, 0, 0
        for i in records_list:
            text += f'{i.calories} / {i.proteins} / {i.fats} / {i.carbohydrates}\n'
            t_cal += i.calories
            t_prot += i.proteins
            t_fats += i.fats
            t_carb += i.carbohydrates
        text += f'\nTotals:\ncalories: {t_cal}\nproteins: {t_prot}\nfats: {t_fats}\ncarbohydrates: {t_carb}'
        if callback.message.text != text:
            await callback.message.edit_text(text, reply_markup=refresh_keyb)
    elif callback.message.text != 'You have no records today':
        await callback.message.edit_text('You have no records today', reply_markup=refresh_keyb)


@cb_router.callback_query(F.data == 'close')
async def cb_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
