from django.contrib import admin
from .models import Category, Blog


admin.site.register(Category)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'registration_datetime', 'display_category')
    list_filter = ['registration_datetime']
