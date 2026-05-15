from django.contrib import admin

from .models import AdBrief, AdCreative, AdVariant, Asset, Campaign, Notification, Project

admin.site.register(Project)
admin.site.register(Asset)
admin.site.register(AdCreative)
admin.site.register(AdBrief)
admin.site.register(AdVariant)
admin.site.register(Campaign)
admin.site.register(Notification)
