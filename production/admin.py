'''
Admin do app production.

Sprint 3: GridProduction.
Sprint 4: MachineStop (paradas de máquina) + inline no GridProduction.
'''

from django.contrib import admin

from production.models import GridProduction, MachineStop


class MachineStopInline(admin.TabularInline):
    model = MachineStop
    extra = 0
    readonly_fields = ('duration_hours', 'duration_label')
    filter_horizontal = ('reasons',)
    fields = ('stop_start', 'stop_end', 'reasons', 'note', 'duration_label')


@admin.register(GridProduction)
class GridProductionAdmin(admin.ModelAdmin):
    list_display = (
        'production_date', 'machine', 'operator', 'shift', 'grid_model',
        'polarity', 'lot', 'quantity', 'production_per_hour', 'stop_hours',
        'created_at',
    )
    list_filter = (
        'production_date', 'machine', 'shift', 'grid_model', 'polarity',
    )
    search_fields = ('lot', 'operator__name', 'grid_model__name')
    list_editable = ()
    readonly_fields = ('lot', 'duration_hours', 'stop_hours', 'effective_hours', 'production_per_hour', 'created_at', 'updated_at')
    date_hierarchy = 'production_date'
    list_select_related = ('operator', 'machine', 'shift', 'grid_model')
    ordering = ('-production_date', '-start_time')
    inlines = [MachineStopInline]


@admin.register(MachineStop)
class MachineStopAdmin(admin.ModelAdmin):
    list_display = (
        'stop_start', 'stop_end', 'duration_label', 'grid_production',
        'reasons_display', 'created_at',
    )
    list_filter = ('stop_start', 'grid_production__machine', 'reasons__category')
    search_fields = ('note', 'grid_production__lot', 'grid_production__operator__name')
    readonly_fields = ('duration_hours', 'duration_label', 'created_at', 'updated_at')
    filter_horizontal = ('reasons',)
    list_select_related = ('grid_production',)
    date_hierarchy = 'stop_start'
    ordering = ('-stop_start',)

    def reasons_display(self, obj):
        return obj.reasons_display
    reasons_display.short_description = 'Motivo(s)'