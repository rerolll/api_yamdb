# Generated by Django 3.2.16 on 2023-08-30 07:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="confirmation_code",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Код подтверждения",
            ),
        ),
    ]
