from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'published_date')
    search_fields = ('title', 'short_description')
    list_filter = ('category',)
