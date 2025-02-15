from django.contrib import admin
from .models import NaatVideo

# Register your models here.

@admin.register(NaatVideo)
class NaatVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_link','tags')  # Admin panel me title aur video link dikhayega
    search_fields = ('title', 'tags')  # Search bar me title ke basis pe search kar sakega


