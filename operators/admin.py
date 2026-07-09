'''
Admin do app operators (RF-A01/A02): list_display, list_filter, search_fields.
'''

from django.contrib import admin

from operators.models import Operator


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'user__email', 'user__username')
    list_editable = ('is_active',)
    autocomplete_fields = ('user',)
    list_per_page = 25
    ordering = ('name',)