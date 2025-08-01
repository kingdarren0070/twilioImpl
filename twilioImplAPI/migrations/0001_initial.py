# Generated by Django 5.2.4 on 2025-07-27 09:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=20)),
                ('communication_preference', models.CharField(choices=[('SMS', 'SMS'), ('Voice', 'Voice')], default='SMS', max_length=5)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logins', to='twilioImplAPI.user')),
            ],
            options={
                'db_table': 'login',
            },
        ),
    ]
