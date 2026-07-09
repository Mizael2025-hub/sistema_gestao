'''URLs do app catalogs — index de cadastros + CRUD de cada entidade.'''
from django.urls import path
from django.views.generic import TemplateView

from catalogs import views

app_name = 'catalogs'


CATALOG_VIEWS = {
    'shift': (views.ShiftListView, views.ShiftDetailView, views.ShiftCreateView, views.ShiftUpdateView, views.ShiftDeleteView),
    'sector': (views.SectorListView, views.SectorDetailView, views.SectorCreateView, views.SectorUpdateView, views.SectorDeleteView),
    'machine': (views.MachineListView, views.MachineDetailView, views.MachineCreateView, views.MachineUpdateView, views.MachineDeleteView),
    'gridmodel': (views.GridModelListView, views.GridModelDetailView, views.GridModelCreateView, views.GridModelUpdateView, views.GridModelDeleteView),
    'leadalloy': (views.LeadAlloyListView, views.LeadAlloyDetailView, views.LeadAlloyCreateView, views.LeadAlloyUpdateView, views.LeadAlloyDeleteView),
    'stopreason': (views.StopReasonListView, views.StopReasonDetailView, views.StopReasonCreateView, views.StopReasonUpdateView, views.StopReasonDeleteView),
}


urlpatterns = [
    path('', TemplateView.as_view(template_name='catalogs/index.html', extra_context={
        'page_title': 'Cadastros-base',
        'page_subtitle': 'Turnos, setores, máquinas, modelos, ligas e motivos de parada',
        'page_icon': 'settings-2',
    }), name='index'),
]

for key, (LV, DV, CV, UV, DV2) in CATALOG_VIEWS.items():
    urlpatterns += [
        path('%s/' % key, LV.as_view(), name='%s_list' % key),
        path('%s/novo/' % key, CV.as_view(), name='%s_create' % key),
        path('%s/<int:pk>/' % key, DV.as_view(), name='%s_detail' % key),
        path('%s/<int:pk>/editar/' % key, UV.as_view(), name='%s_update' % key),
        path('%s/<int:pk>/excluir/' % key, DV2.as_view(), name='%s_delete' % key),
    ]