import datetime

from django.db import models
from django.utils import timezone


class User(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='Id пользователя')
    username = models.CharField(max_length=128, verbose_name='Ник пользователя')
    referral = models.ManyToManyField('self', blank=True, verbose_name='Рефералы')
    referral_count = models.IntegerField(default=0, verbose_name='Количество рефералов за все время')
    referral_per_day = models.IntegerField(default=0, verbose_name='Рефералы за день')
    balance = models.FloatField(default=0, verbose_name='Баланс пользователя')
    freeze_balance = models.FloatField(default=0, verbose_name='Замороженный баланс пользователя')
    complete_first_task = models.BooleanField(default=False, verbose_name='Подписался ли на первые каналы?')
    tasks = models.ManyToManyField('UserTask', blank=True, verbose_name='Задания пользователя')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом?')
    use_day_bonus = models.BooleanField(default=False, verbose_name='Использовал ли дневной бонус?')

    def __str__(self):
        if self.username:
            return self.username
        return self.chat_id



class UserTask(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, verbose_name='Задача', related_name='users_task')
    end_time = models.DateTimeField(default=timezone.now()+datetime.timedelta(days=1), verbose_name='Дата окончания задачи')

class Task(models.Model):
    url = models.URLField(verbose_name='Ссылка на канал, на который надо подписаться')
    channel_id = models.CharField(max_length=128, verbose_name='ID канала')
    reward = models.FloatField(default=0, verbose_name='Награда за задание')
    is_close = models.BooleanField(default=False, verbose_name='Закрытый ли канал?')
    is_first_task = models.BooleanField(default=False, verbose_name='Явяляется ли это задание необходимым для входа в бота?')


class Refferal_reward(models.Model):
    reward = models.FloatField(default=1, verbose_name='Награда за реферала')


class DayReward(models.Model):
    reward = models.FloatField(default=1.5, verbose_name='Награда')
    min_referral = models.IntegerField(default=5, verbose_name='Минимальное количество рефералов в день.')


class Promocode(models.Model):
    name = models.CharField(max_length=32, verbose_name='Название промокода')
    reward = models.IntegerField(default=10, verbose_name='Награда за промокод')
    max_user = models.IntegerField(default=100, verbose_name='Количество использований')
    min_referral = models.IntegerField(default=0, verbose_name='Минимальное количество рефералов')
    users = models.ManyToManyField('User', blank=True, verbose_name='Пользователи, использовавшие промокод')
