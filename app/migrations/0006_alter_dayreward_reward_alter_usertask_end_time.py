# Generated by Django 5.1.4 on 2025-01-04 19:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_dayreward_user_use_day_bonus_alter_usertask_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dayreward',
            name='reward',
            field=models.FloatField(default=10, verbose_name='Награда'),
        ),
        migrations.AlterField(
            model_name='usertask',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 5, 19, 23, 53, 91964, tzinfo=datetime.timezone.utc), verbose_name='Дата окончания задачи'),
        ),
    ]
