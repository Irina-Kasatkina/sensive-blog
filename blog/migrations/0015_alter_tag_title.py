# Generated by Django 4.1.1 on 2022-10-05 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_alter_post_options_alter_post_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='title',
            field=models.CharField(db_index=True, max_length=20, unique=True, verbose_name='Тег'),
        ),
    ]
