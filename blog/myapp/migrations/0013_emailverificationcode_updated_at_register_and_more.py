# Generated by Django 5.1 on 2024-09-01 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_alter_emailverificationcode_code_reset'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailverificationcode',
            name='updated_at_register',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emailverificationcode',
            name='updated_at_reset',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
