'''
Admin do app catalogs (RF-A01/A02).
'''

from django.contrib import admin

from catalogs.models import (
    Shift, Sector, Machine, GridModel, LeadAlloy, StopReason,
)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active',)
    ordering = ('name',)


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'is_active', 'created_at', 'updated_at')
    list_filter = ('sector', 'is_active')
    search_fields = ('name', 'sector__name')
    list_editable = ('is_active',)
    autocomplete_fields = ('sector',)
    list_select_related = ('sector',)
    ordering = ('name',)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_overtime', 'start_time', 'end_time', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_overtime')
    search_fields = ('name',)
    list_editable = ('is_active',)
    ordering = ('start_time', 'name')


@admin.register(GridModel)
class GridModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'common_name', 'positive_plates', 'negative_plates', 'shares_grid_with', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'common_name')
    list_editable = ('is_active',)
    autocomplete_fields = ('shares_grid_with',)
    ordering = ('name',)


@admin.register(LeadAlloy)
class LeadAlloyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'color', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    list_editable = ('is_active',)
    ordering = ('code',)


@admin.register(StopReason)
class StopReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'category', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    ordering = ('category', 'description')