# Generated by Django 5.0.7 on 2024-07-26 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_bloginformation_time_comment_delete_customuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bloginformation',
            name='comment',
        ),
    ]
