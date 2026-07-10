'''URLs do app production — Sprint 3 (Teleiras) + Sprint 4 (Paradas) + Sprint 5 (Empaste).'''
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
]