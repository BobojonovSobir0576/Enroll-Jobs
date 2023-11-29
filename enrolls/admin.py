from django.contrib import admin

from enrolls.models import (
    JobCategories,
    JobVacancies,
    JobApply,
    JobAttachment,
    StatusApply
)

admin.site.register(JobCategories)
admin.site.register(JobVacancies)
admin.site.register(JobApply)
admin.site.register(StatusApply)
admin.site.register(JobAttachment)

