# Generated by Django 3.2.9 on 2022-01-22 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0004_alter_comment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='type',
            field=models.CharField(choices=[('default', 'default'), ('quote', 'quote'), ('answer', 'reply')], default='default', max_length=16),
        ),
    ]
