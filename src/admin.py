from django.contrib import admin
from . import models
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(models.App, SimpleHistoryAdmin)
admin.site.register(models.ToOrganisation)
admin.site.register(models.FindingTypes)
admin.site.register(models.FindingStatus)
admin.site.register(models.FindingSeverity)
admin.site.register(models.EPAFinding)
admin.site.register(models.SCASFinding)
admin.site.register(models.SPFinding)
admin.site.register(models.LCSAFinding)

