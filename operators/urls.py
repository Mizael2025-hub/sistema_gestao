'''URLs do app operators (UI sob /operadores).'''
from django.urls import path

from operators import views

app_name = 'operators'

urlpatterns = [
    path('', views.OperatorListView.as_view(), name='operator_list'),
    path('novo/', views.OperatorCreateView.as_view(), name='operator_create'),
    path('<int:pk>/', views.OperatorDetailView.as_view(), name='operator_detail'),
    path('<int:pk>/editar/', views.OperatorUpdateView.as_view(), name='operator_update'),
    path('<int:pk>/excluir/', views.OperatorDeleteView.as_view(), name='operator_delete'),
]