'''
Admin do app production.

Sprint 3: GridProduction.
Sprint 4: MachineStop (paradas de máquina) + inline no GridProduction.
Sprint 5: PasteProduction (empaste) + inline de OxideConsumption.
Sprint 6: MassProduction, Assembly, Formation (masseira, montagem, formação).
'''

from django.contrib import admin

from production.models import (
    Assembly, Formation, GridProduction, MachineStop, MassProduction, OxideConsumption, PasteProduction,
)


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


class OxideConsumptionInline(admin.StackedInline):
    model = OxideConsumption
    extra = 0
    max_num = 1
    verbose_name = 'consumo de óxido'
    verbose_name_plural = 'consumo de óxido'


@admin.register(PasteProduction)
class PasteProductionAdmin(admin.ModelAdmin):
    list_display = (
        'paste_date', 'grid_model', 'polarity', 'lot', 'pasted_quantity',
        'panel_loss', 'grid_loss', 'effective_quantity', 'oxide_weight',
        'created_at',
    )
    list_filter = ('paste_date', 'grid_model', 'polarity')
    search_fields = ('lot', 'grid_model__name')
    readonly_fields = ('lot', 'effective_quantity', 'oxide_weight', 'created_at', 'updated_at')
    list_select_related = ('grid_model', 'oxide_consumption')
    date_hierarchy = 'paste_date'
    ordering = ('-paste_date', '-id')
    inlines = [OxideConsumptionInline]

    def oxide_weight(self, obj):
        return obj.oxide_weight
    oxide_weight.short_description = 'Óxido (kg)'


# --------------------------------------------------------------------- #
# Sprint 6 — Masseira, Montagem, Formação
# --------------------------------------------------------------------- #
@admin.register(MassProduction)
class MassProductionAdmin(admin.ModelAdmin):
    list_display = (
        'mass_date', 'lead_lot', 'polarity', 'weight', 'discarded_weight',
        'mass_remainder_weight', 'oxide_excess_weight', 'ready_mass_excess_weight',
        'additive_weight', 'balance_weight', 'created_at',
    )
    list_filter = ('mass_date', 'polarity')
    search_fields = ('lead_lot',)
    list_select_related = ()
    date_hierarchy = 'mass_date'
    ordering = ('-mass_date', '-id')


@admin.register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    list_display = (
        'assembly_date', 'grid_model', 'lot', 'quantity', 'positive_ep',
        'negative_ep', 'created_at',
    )
    list_filter = ('assembly_date', 'grid_model')
    search_fields = ('lot', 'grid_model__name', 'positive_ep__lot', 'negative_ep__lot', 'note')
    list_select_related = ('grid_model', 'positive_ep', 'negative_ep')
    date_hierarchy = 'assembly_date'
    ordering = ('-assembly_date', '-id')
    autocomplete_fields = ('positive_ep', 'negative_ep')


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = (
        'formation_date', 'table_number', 'battery_lot', 'grid_model',
        'quantity', 'created_at',
    )
    list_filter = ('formation_date', 'grid_model', 'table_number')
    search_fields = ('battery_lot', 'grid_model__name')
    list_select_related = ('grid_model',)
    date_hierarchy = 'formation_date'
    ordering = ('-formation_date', '-table_number')