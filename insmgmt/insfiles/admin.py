from django.contrib import admin

from .models import Client, Scan, ExtensionType, ExtensionField

admin.site.register(Client)
admin.site.register(Scan)
admin.site.register(ExtensionType)
admin.site.register(ExtensionField)