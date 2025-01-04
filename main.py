import os
import random
import threading
import time

import django
from django.utils import timezone

import buttons

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StarsBot.settings')
django.setup()
from const import bot
from app.models import User, Task, UserTask, Refferal_reward, Promocode, DayReward

Refferal_reward.objects.get_or_create(id=1)
DayReward.objects.get_or_create(id=1)


def check_subscribes():
    while True:
        for user in User.objects.all():
            for task in user.tasks.all():
                if timezone.now().timestamp() < task.end_time.timestamp():
                    if not check_subscribe(chat_id=user.chat_id, channel_id=task.task.channel_id):
                        bot.send_message(chat_id=user.chat_id,
                                         text=f'С вашего баланса списано {task.task.reward}⭐️ за отписку от канала в течении 24 часов')
                        user.balance -= task.task.reward
                        user.save(update_fields=['balance'])
                        task.delete()
                else:
                    task.delete()
        time.sleep(60 * 30)


def null_day_ref():
    while True:
        for user in User.objects.all():
            user.referral_per_day = 0
            user.save(update_fields=['referral_per_day'])
        time.sleep(60 * 60 * 24)


def check_subscribe(chat_id, channel_id):
    try:
        n = bot.get_chat_member(chat_id=channel_id, user_id=chat_id)
        if n.status == 'left':
            return False
    except Exception:
        return False
    return True


def check_start_subscrbe(user):
    for task in Task.objects.filter(is_first_task=True):
        if not check_subscribe(user.chat_id, task.channel_id):
            user.complete_first_task = False
            user.save(update_fields=['complete_first_task'])
            return False
    user.complete_first_task = True
    user.save(update_fields=['complete_first_task'])
    return True


def not_subscribed(chat_id):
    bot.send_message(chat_id=chat_id, text='Вам необходимо подписаться на канал, чтобы пользоваться ботом.',
                     reply_markup=buttons.not_subscribed())


def tasks(chat_id):
    text = '✅Выполняй задания и получай за это звезды 🌟'
    bot.send_photo(chat_id=chat_id, photo=open('photos/task.jpg', 'rb'), caption=text, reply_markup=buttons.tasks())


def detail_task(chat_id, task_id):
    text = '🎯Доступно задание подписаться!'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.task_dtail(task_id))


def collect_stars(chat_id):
    reward = Refferal_reward.objects.all().first().reward
    text = f'Получи {reward} ⭐️ за каждого приглашенного тобой пользователя‼️\n\n' \
           f'По ней ты должен приглашать друзей/знакомых 💫\n' \
           f'Ну или отправлять свою ссылку различных чатах\n' \
           f'Твоя реферальная ссылка 🔗: `https://t.me/{bot.get_me().username}?start={chat_id}`'

    bot.send_photo(chat_id=chat_id, photo=open('photos/collect_stars.jpg', 'rb'), caption=text, parse_mode='MarkDownV2')


@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    if not username:
        username = 'Анонимный пользователь'
    user, _ = User.objects.get_or_create(chat_id=message.from_user.id, username=username)
    if _ and len(message.text.split()) == 2:
        ref = User.objects.filter(chat_id=message.text.split()[1]).first()
        if ref:
            ref.referral.add(user)
            ref.referral_count += 1
            ref.referral_per_day += 1
            ref.balance += Refferal_reward.objects.all().first().reward
            ref.save(update_fields=['referral_count', 'referral_per_day'])
    not_subscribed(chat_id=user.chat_id)


def menu(chat_id):
    bot.send_message(chat_id=chat_id, text='Главное меню', reply_markup=buttons.buttons())


def top(chat_id, param, text):
    users = list(User.objects.all().order_by(f'-{param}'))[:10]
    text = f'Топ 10 рефералов за {text}:\n\n'
    if 'все время' in text:
        for i, user in enumerate(users, start=1):
            text += f'{i}. @{user.username} - {user.referral_count} рефералов\n'
        bot.send_photo(chat_id=chat_id, photo=open('photos/top.jpg', 'rb'), caption=text)
    else:
        for i, user in enumerate(users, start=1):
            text += f'{i}. @{user.username} - {user.referral_per_day} рефералов\n'
        bot.send_photo(chat_id=chat_id, photo=open('photos/top_24.jpg', 'rb'), caption=text)


def profile(user):
    text = f'👤Мой профиль\n\n'
    text += f'Статистика ⤵️\n\n'
    text += f'✨ Приглашенных за 24 часа:: {user.referral_per_day}\n\n'
    text += f'📈 Приглашенных за все время: {user.referral_per_day}\n\n'
    text += f'🌟Баланс: 🌟 {round(user.balance, 2)}⭐️️\n\n'
    bot.send_photo(chat_id=user.chat_id, photo=open('photos/profile.jpg', 'rb'), caption=text)


def exit_stars(message, user):
    if message.content_type == 'text':
        if message.text in ['Заработать звезды ⭐', 'Профиль 👤', 'рассылка', 'Топ пользователей 📊', 'Задания 📚',
                            'Вывести звезды 🌟', 'Промокод 🎁', 'Ежедневный бонус ⏰']:
            text_handler(None, message.text, user.chat_id)
        else:
            try:
                error = 'Мы выводим только выводы на суммы: 15 ⭐️, 25 ⭐️, 50 ⭐️, 100 ⭐️ и выше'
                stars = int(message.text)
                if stars > user.balance:
                    error = 'У вас недостаточно звезд на балансе'
                    raise Exception
                if stars < 100 and stars not in [15, 25, 50, 100]:
                    raise Exception
            except Exception:
                msg = bot.send_message(chat_id=user.chat_id, text=error, reply_markup=buttons.go_to_menu())
                bot.register_next_step_handler(msg, exit_stars, user)
            else:
                user.balance -= stars
                user.freeze_balance += stars
                user.save(update_fields=['balance', 'freeze_balance'])
                admin = random.choice(User.objects.filter(is_admin=True))
                bot.send_message(chat_id=admin.chat_id, text=f'Заявка на вывод {stars}⭐️',
                                 reply_markup=buttons.admin_message(stars=stars, chat_id=user.chat_id))


def mailing(message):
    message_id = message.id
    from_chat_id = message.chat.id
    for user in User.objects.all():
        try:
            bot.copy_message(message_id=message_id, chat_id=user.chat_id, from_chat_id=from_chat_id)
        except Exception:
            continue


def promocode(message, user):
    if message.content_type == 'text':
        if message.text in ['Заработать звезды ⭐', 'Профиль 👤', 'рассылка', 'Топ пользователей 📊', 'Задания 📚',
                            'Вывести звезды 🌟', 'Промокод 🎁', 'Ежедневный бонус ⏰']:
            text_handler(None, message.text, user.chat_id)
        else:
            promocode = message.text
            try:
                promo = Promocode.objects.get(name=promocode)
                if user in promo.users.all():
                    bot.send_message(chat_id=user.chat_id, text='Промокод уже использован')
                else:
                    promo.users.add(user)
                    user.balance += promo.reward
                    user.save(update_fields=['balance'])
                    bot.send_message(chat_id=user.chat_id,
                                     text=f'Промокод успешно использован!\nВам начислено {promo.reward}⭐️')
                    if promo.users.all().count() == promo.max_user:
                        promo.delete()
            except Exception:
                bot.send_message(chat_id=user.chat_id, text='Промокод не найден')


def day_bonus(user):
    day_bonus = DayReward.objects.get(id=1)
    if user.referral_per_day >= day_bonus.min_referral:
        user.balance += day_bonus.reward
        user.use_day_bonus = True
        user.save(update_fields=['balance', 'use_day_bonus'])
        bot.send_photo(chat_id=user.chat_id, photo=open('photos/day_bonus.jpg', 'rb'),
                       caption=f'🎁 Вы получили ежедневный бонус в размере {day_bonus.reward} звезды 🌟️')
    else:
        bot.send_photo(chat_id=user.chat_id, photo=open('photos/day_bonus.jpg', 'rb'),
                       caption=f'🎁 Пригласи {day_bonus.min_referral} друзей и получи ежедневный бонус в размере {day_bonus.reward} звезды 🌟')


@bot.message_handler(content_types='text')
def text_handler(message, command=None, chat_id=None):
    if not command:
        chat_id = message.from_user.id
        command = message.text
    user = User.objects.get(chat_id=chat_id)
    if not check_start_subscrbe(user):
        not_subscribed(chat_id=chat_id)
    elif command == 'Заработать звезды ⭐️':
        collect_stars(chat_id=chat_id)
    elif command == 'Профиль 👤':
        profile(user)
    elif command == 'Топ пользователей 📊':
        bot.send_message(chat_id=chat_id, text='Выбери какую статистику хочешь посмотреть👇', reply_markup=buttons.top())
    elif command == 'Задания 📚':
        tasks(chat_id=chat_id)
    elif command == 'Вывести звезды 🌟':
        text = "💳 Минимальная сумма вывода: 15⭐️\n\n" \
               f"Так-же мы выводим только выводы на суммы: 15 ⭐️, 25 ⭐️, 50 ⭐️, 100 ⭐️ и выше\n\n" \
               f"❗️Если ваш вывод на другую сумму, он будет отклонен админом❗️\n\n" \
               "‼️Введите вашу сумму звезд, которую желаете вывести:"
        msg = bot.send_photo(chat_id=chat_id, photo=open('photos/exit_stars.jpg', 'rb'), caption=text)
        bot.register_next_step_handler(msg, exit_stars, user)
    elif command == 'рассылка' and user.is_admin:
        msg = bot.send_message(chat_id=chat_id, text='Введите текст рассылки')
        bot.register_next_step_handler(msg, mailing)
    elif command == 'Промокод 🎁':
        msg = bot.send_photo(chat_id=chat_id, photo=open('photos/promo.jpg', 'rb'),
                             caption='✨Введите промокод, и получите от нас бонус 🎁')
        bot.register_next_step_handler(msg, promocode, user)
    elif command == 'Ежедневный бонус ⏰':
        day_bonus(user)
    elif command == '122222':
        pass


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    user, _ = User.objects.get_or_create(chat_id=chat_id)
    if call.message:
        data = call.data.split('|')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        if not check_start_subscrbe(user):
            not_subscribed(chat_id=chat_id)
        if data[0] == 'check_start_subsctibes':
            menu(chat_id=chat_id)
        elif data[0] == 'task':
            detail_task(chat_id=chat_id, task_id=data[1])
        elif data[0] == 'check_subsctibe':
            task = Task.objects.get(id=data[1])
            if check_subscribe(chat_id=chat_id, channel_id=task.channel_id):
                if not user.tasks.filter(task=task).exists():
                    user.tasks.add(UserTask.objects.create(task=task))
                    reward = task.reward
                    user.balance += reward
                    user.save(update_fields=['balance'])
                    bot.send_message(chat_id=chat_id, text='Баланс успешно пополнен')
                else:
                    bot.send_message(chat_id=chat_id, text='Вы уже сделали это задание')
                time.sleep(1)
                tasks(chat_id=chat_id)
            else:
                bot.send_message(chat_id=chat_id, text='Вам нужно подписаться на канал')
                time.sleep(1)
                detail_task(chat_id=chat_id, task_id=data[1])
        elif data[0] == 'tasks':
            tasks(chat_id=chat_id)
        elif data[0] == 'all_top':
            top(chat_id=chat_id, param='referral_count', text='все время')
        elif data[0] == 'day_top':
            top(chat_id=chat_id, param='referral_per_day', text='все 24 часа')
        elif data[0] == 'back':
            menu(chat_id=chat_id)
        elif data[0] == 'approve':
            usr = User.objects.get(chat_id=data[1])
            usr.freeze_balance -= int(data[2])
            usr.save(update_fields=['freeze_balance'])
            bot.send_message(chat_id=usr.chat_id, text='Ваша заявка на вывод одобрена✅'
                                                       'Ожидайте пополнения в течении 24 часов 🚀')
        elif data[0] == 'cansel':
            usr = User.objects.get(chat_id=data[1])
            usr.freeze_balance -= int(data[2])
            usr.balance += int(data[2])
            usr.save(update_fields=['freeze_balance', 'balance'])
            bot.send_message(chat_id=usr.chat_id, text='Ваша заявка на вывод отклонена')


if __name__ == '__main__':
    polling_thread1 = threading.Thread(target=null_day_ref)
    polling_thread1.start()
    polling_thread2 = threading.Thread(target=check_subscribes)
    polling_thread2.start()
    bot.infinity_polling(timeout=50, long_polling_timeout=25)
