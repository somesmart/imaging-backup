from django.contrib import admin

from .models import Client, Scan

admin.site.register(Client)
admin.site.register(Scan)