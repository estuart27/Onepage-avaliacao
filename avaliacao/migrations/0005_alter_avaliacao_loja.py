# Generated by Django 5.0.2 on 2024-11-12 18:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacao', '0004_loja_shopping_alter_avaliacao_loja_loja_shopping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avaliacao',
            name='loja',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='avaliacao.loja'),
        ),
    ]
