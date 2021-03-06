# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-11 07:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('followed_user_id', models.BigIntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('is_completed', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('screen_name', models.CharField(db_index=True, max_length=256, unique=True)),
                ('name', models.CharField(max_length=256)),
                ('profile_image_url', models.URLField(max_length=1024)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=256)),
                ('followers_count', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='follower',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitter_wrapper.User'),
        ),
        migrations.AlterUniqueTogether(
            name='follower',
            unique_together=set([('followed_user_id', 'follower')]),
        ),
        migrations.AlterIndexTogether(
            name='follower',
            index_together=set([('followed_user_id', 'follower')]),
        ),
    ]
