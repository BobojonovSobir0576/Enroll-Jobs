# Generated by Django 4.2.7 on 2023-11-29 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('enrolls', '0008_alter_jobvacancies_job_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapply',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL),
        ),
    ]