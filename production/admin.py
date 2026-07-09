'''Admin do app production — Sprint 3: GridProduction (RF-A01/A02).'''

from django.contrib import admin

from production.models import GridProduction


@admin.register(GridProduction)
class GridProductionAdmin(admin.ModelAdmin):
    list_display = (
        'production_date', 'machine', 'operator', 'shift', 'grid_model',
        'polarity', 'lot', 'quantity', 'production_per_hour', 'created_at',
    )
    list_filter = (
        'production_date', 'machine', 'shift', 'grid_model', 'polarity',
    )
    search_fields = ('lot', 'operator__name', 'operator__registration', 'grid_model__name')
    list_editable = ()
    readonly_fields = ('lot', 'duration_hours', 'effective_hours', 'production_per_hour', 'created_at', 'updated_at')
    date_hierarchy = 'production_date'
    list_select_related = ('operator', 'machine', 'shift', 'grid_model')
    ordering = ('-production_date', '-start_time')