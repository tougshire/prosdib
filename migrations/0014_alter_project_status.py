# Generated by Django 3.2.9 on 2022-05-26 00:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prosdib', '0013_alter_status_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.ForeignKey(default=1, help_text='The status of this project', null=True, on_delete=django.db.models.deletion.SET_NULL, to='prosdib.status', verbose_name='status'),
        ),
    ]