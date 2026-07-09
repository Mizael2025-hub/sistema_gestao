'''
Mixins de views compartilhados.

- BaseViewContext: injeta breadcrumbs e título de página.
- FilteredListView: listagem com filtros via GET (form) e paginação opcional.
'''

from django.views.generic import ListView


class PageContextMixin:
    '''Adiciona page_title e page_subtitle ao contexto.'''

    page_title = ''
    page_subtitle = ''
    page_icon = ''  # nome do ícone lucide

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.page_title
        ctx['page_subtitle'] = self.page_subtitle
        ctx['page_icon'] = self.page_icon
        return ctx


class FilteredListMixin:
    '''
    Aplica um form de filtros (filter_form_class) sobre o queryset.

    O form deve receber GET como data e expor método filter_queryset(qs).
    '''

    filter_form_class = None
    filter_form = None

    def get_queryset(self):
        qs = super().get_queryset()
        form = self.get_filter_form()
        if form.is_valid():
            qs = form.filter_queryset(qs)
        return qs

    def get_filter_form(self):
        if self.filter_form is None:
            self.filter_form = self.filter_form_class(self.request.GET or None)
        return self.filter_form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = self.get_filter_form()
        ctx['filters_active'] = any(
            v for v in self.get_filter_form().cleaned_data.values()
        ) if self.get_filter_form().is_valid() else False
        return ctx