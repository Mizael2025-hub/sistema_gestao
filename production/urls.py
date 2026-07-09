'''URLs do app production — Sprint 3: Teleiras.'''
from django.urls import path

from production import views

app_name = 'production'

urlpatterns = [
    path('teleiras/', views.GridProductionListView.as_view(), name='gridproduction_list'),
    path('teleiras/novo/', views.GridProductionCreateView.as_view(), name='gridproduction_create'),
    path('teleiras/<int:pk>/', views.GridProductionDetailView.as_view(), name='gridproduction_detail'),
    path('teleiras/<int:pk>/editar/', views.GridProductionUpdateView.as_view(), name='gridproduction_update'),
]