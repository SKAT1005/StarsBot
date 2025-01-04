# Generated by Django 5.1.4 on 2025-01-03 00:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_task_channel_id_alter_usertask_end_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refferal_reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward', models.IntegerField(default=2, verbose_name='Награда за реферала')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Является ли пользователь админом?'),
        ),
        migrations.AlterField(
            model_name='usertask',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2025, 1, 4, 0, 32, 27, 786342, tzinfo=datetime.timezone.utc), verbose_name='Дата окончания задачи'),
        ),
    ]
