import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StarsBot.settings')
django.setup()
from app.models import User, Task, UserTask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def buttons():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    get_stars = KeyboardButton('Заработать звезды ⭐️')
    profile = KeyboardButton('Профиль 👤')
    top = KeyboardButton('Топ пользователей 📊')
    task = KeyboardButton('Задания 📚')
    get_reward = KeyboardButton('Вывести звезды 🌟')
    promo = KeyboardButton('Промокод 🎁')
    day_bonus = KeyboardButton('Ежедневный бонус ⏰')
    markup.add(get_stars)
    markup.add(profile, top, task, promo, get_reward, day_bonus)
    return markup


def not_subscribed():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for _, task in enumerate(Task.objects.filter(is_first_task=True), start=1):
        tasks = InlineKeyboardButton(text=f'Спонсор №{_}', url=task.url)
        buttons.append(tasks)

    # Разделяем список кнопок на ряды по два элемента
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i + 2])  # Используем * для распаковки списка в аргументы add

    markup.add(InlineKeyboardButton('✅ Проверить подписку', callback_data='check_start_subsctibes'))
    return markup


def tasks():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for task in Task.objects.filter(is_first_task=False):
        tasks = InlineKeyboardButton(text=f'Спонсор №{task.id}', callback_data=f'task|{task.id}')
        buttons.append(tasks)

    # Разделяем список кнопок на ряды по два элемента
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i + 2])
    return markup


def task_dtail(task_id):
    task = Task.objects.get(id=task_id)
    markup = InlineKeyboardMarkup(row_width=1)
    url = InlineKeyboardButton('Канал', url=task.url)
    check = InlineKeyboardButton('Поверить подписку', callback_data=f'check_subsctibe|{task.id}')
    back = InlineKeyboardButton('Назад', callback_data='tasks')
    markup.add(url, check, back)
    return markup


def top():
    markup = InlineKeyboardMarkup(row_width=1)
    stat_button = InlineKeyboardButton('Топ за все время', callback_data='all_top')
    back = InlineKeyboardButton('Топ за 24 часа', callback_data='day_top')
    markup.add(stat_button, back)
    return markup


def admin_message(stars, chat_id):
    markup = InlineKeyboardMarkup(row_width=1)
    profile = InlineKeyboardButton('Профиль', url=f'tg://user?id={chat_id}')
    approve = InlineKeyboardButton('Подтвердить вывод', callback_data=f'approve|{chat_id}|{stars}')
    cansel = InlineKeyboardButton('Отказать в выводе', callback_data=f'cansel|{chat_id}|{stars}')
    markup.add(profile, approve, cansel)
    return markup



def go_to_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    back = InlineKeyboardButton('Назад', callback_data='back')
    markup.add(back)
    return markup
