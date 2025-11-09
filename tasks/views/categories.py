from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from tasks.forms import CategorySearchForm, CategoryForm
from tasks.mixins import CoordinatorRequiredMixin
from tasks.models import Category


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name")
        context["search_form"] = CategorySearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        queryset = Category.objects.all()
        form = CategorySearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = Category


class CategoryCreateView(LoginRequiredMixin,
                         CoordinatorRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("tasks:category-list")


class CategoryUpdateView(LoginRequiredMixin,
                         CoordinatorRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("tasks:category-list")


class CategoryDeleteView(LoginRequiredMixin,
                         CoordinatorRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("tasks:category-list")
