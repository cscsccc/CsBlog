# Generated by Django 5.1 on 2024-08-31 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_emailverificationcode_code_register_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverificationcode',
            name='code_reset',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
