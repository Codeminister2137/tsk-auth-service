# Generated by Django 5.1.5 on 2025-02-05 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_rename_special_role_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(default='user', max_length=100),
        ),
    ]
