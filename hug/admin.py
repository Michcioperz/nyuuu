from django.contrib import admin
from .models import Hug, BonusData


@admin.register(Hug)
class HugAdmin(admin.ModelAdmin):
    list_display = ('pk', 'source', 'target', 'timestamp', 'inspiration',)

admin.site.register(BonusData)
