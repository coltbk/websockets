# Generated by Django 4.2.8 on 2024-03-31 21:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sensorreading",
            name="param",
            field=models.CharField(default="unk", max_length=10),
        ),
    ]
