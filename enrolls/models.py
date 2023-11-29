from django.db import models
from django.contrib.auth.models import User


class JobCategories(models.Model):
    tag = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.tag


class JobVacancies(models.Model):
    job_category = models.ForeignKey(
        JobCategories, on_delete=models.CASCADE,
        null=True, blank=True, related_name='categor_id'
    )
    title = models.CharField(
        max_length=255,
        null=True, blank=True
    )
    description = models.TextField(
        null=True, blank=True
    )
    price = models.FloatField(
        default=0, null=True,
        blank=True
    )
    created_at = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class JobApply(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True, blank=True
    )
    jobs = models.ForeignKey(
        JobVacancies, on_delete=models.CASCADE,
        null=True, blank=True
    )
    created_at = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.user.username}'


class JobAttachment(models.Model):
    job_apply = models.ForeignKey(
        JobApply, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='apply_jobs_user'
    )
    attachment = models.FileField(
        upload_to='attachment',
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.job_apply.user.username}"
