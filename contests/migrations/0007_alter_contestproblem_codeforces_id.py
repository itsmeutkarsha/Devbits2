# Generated by Django 5.1.6 on 2025-03-02 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0006_remove_contest_is_private_contest_problems_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestproblem',
            name='codeforces_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
