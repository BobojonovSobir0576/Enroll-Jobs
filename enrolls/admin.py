from django.contrib import admin

from enrolls.models import (
    JobCategories,
    JobVacancies,
    JobApply,
    JobAttachment
)

admin.site.register(JobCategories)
admin.site.register(JobVacancies)
admin.site.register(JobApply)
admin.site.register(JobAttachment)

