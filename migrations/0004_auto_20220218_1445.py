# Generated by Django 3.2.9 on 2022-02-18 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prosdib', '0003_auto_20220217_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectnote',
            name='is_major',
            field=models.BooleanField(default=False, help_text='If this note is diplayed by default in the project detail view.  If not, it will be displayed when "Show All" is selected', verbose_name='is major or current status'),
        ),
        migrations.AddField(
            model_name='projectnote',
            name='time_spent',
            field=models.IntegerField(default=0, help_text='The amount of time to be added to the project as per this note', verbose_name='time spent'),
        ),
    ]
