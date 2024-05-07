from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

refresh_keyb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Refresh data', callback_data='refresh')]])
start_keyb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Today data', callback_data='refresh')],
                                                   [InlineKeyboardButton(text='X', callback_data='close')]])
