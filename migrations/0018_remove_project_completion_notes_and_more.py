# Generated by Django 4.1.2 on 2023-01-15 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prosdib', '0017_rename_text_projectnote_maintext_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='completion_notes',
        ),
        migrations.RemoveField(
            model_name='project',
            name='time_spent',
        ),
    ]