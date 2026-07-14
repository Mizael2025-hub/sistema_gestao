'''URLs do app production — Sprint 3..6 (Teleiras, Paradas, Empaste, Masseira, Montagem, Formação).'''
from django.urls import path

from production import views

app_name = 'production'

urlpatterns = [
    # Sprint 3 — Teleiras
    path('teleiras/', views.GridProductionListView.as_view(), name='gridproduction_list'),
    path('teleiras/novo/', views.GridProductionCreateView.as_view(), name='gridproduction_create'),
    path('teleiras/<int:pk>/', views.GridProductionDetailView.as_view(), name='gridproduction_detail'),
    path('teleiras/<int:pk>/editar/', views.GridProductionUpdateView.as_view(), name='gridproduction_update'),

    # Sprint 4 — Paradas de máquina
    path('paradas/', views.MachineStopListView.as_view(), name='machinestop_list'),
    path('paradas/localizar/', views.MachineStopLocateView.as_view(), name='machinestop_locate'),
    path('paradas/novo/', views.MachineStopCreateView.as_view(), name='machinestop_create'),
    path('paradas/<int:pk>/', views.MachineStopDetailView.as_view(), name='machinestop_detail'),
    path('paradas/<int:pk>/editar/', views.MachineStopUpdateView.as_view(), name='machinestop_update'),
    path('paradas/<int:pk>/excluir/', views.MachineStopDeleteView.as_view(), name='machinestop_delete'),

    # Sprint 5 — Empaste e consumos (RF-E01..E04)
    path('empaste/', views.PasteProductionListView.as_view(), name='pasteproduction_list'),
    path('empaste/novo/', views.PasteProductionCreateView.as_view(), name='pasteproduction_create'),
    path('empaste/<int:pk>/', views.PasteProductionDetailView.as_view(), name='pasteproduction_detail'),
    path('empaste/<int:pk>/editar/', views.PasteProductionUpdateView.as_view(), name='pasteproduction_update'),
    path('empaste/<int:pk>/excluir/', views.PasteProductionDeleteView.as_view(), name='pasteproduction_delete'),

    # Sprint 6 — Masseira (RF-M01)
    path('masseira/', views.MassProductionListView.as_view(), name='massproduction_list'),
    path('masseira/novo/', views.MassProductionCreateView.as_view(), name='massproduction_create'),
    path('masseira/<int:pk>/', views.MassProductionDetailView.as_view(), name='massproduction_detail'),
    path('masseira/<int:pk>/editar/', views.MassProductionUpdateView.as_view(), name='massproduction_update'),
    path('masseira/<int:pk>/excluir/', views.MassProductionDeleteView.as_view(), name='massproduction_delete'),

    # Sprint 6 — Montagem (RF-MO01)
    path('montagem/', views.AssemblyListView.as_view(), name='assembly_list'),
    path('montagem/novo/', views.AssemblyCreateView.as_view(), name='assembly_create'),
    path('montagem/<int:pk>/', views.AssemblyDetailView.as_view(), name='assembly_detail'),
    path('montagem/<int:pk>/editar/', views.AssemblyUpdateView.as_view(), name='assembly_update'),
    path('montagem/<int:pk>/excluir/', views.AssemblyDeleteView.as_view(), name='assembly_delete'),

    # Sprint 6 — Formação (RF-F01..F02)
    path('formacao/', views.FormationListView.as_view(), name='formation_list'),
    path('formacao/novo/', views.FormationCreateView.as_view(), name='formation_create'),
    path('formacao/importar/', views.FormationImportView.as_view(), name='formation_import'),
    path('formacao/<int:pk>/', views.FormationDetailView.as_view(), name='formation_detail'),
    path('formacao/<int:pk>/editar/', views.FormationUpdateView.as_view(), name='formation_update'),
    path('formacao/<int:pk>/excluir/', views.FormationDeleteView.as_view(), name='formation_delete'),
]