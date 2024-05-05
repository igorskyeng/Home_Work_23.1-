from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy, reverse
from django.forms import inlineformset_factory
from main.forms import ProductForm, VersionForm, ModeratorFormProducts, ProductAddForm

from pytils.translit import slugify

from main.models import Product, Version


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    permission_required = 'main.add_product'
    form_class = ProductAddForm
    success_url = reverse_lazy('main:index')

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        VersionFormset = inlineformset_factory(Product, Version, form=VersionForm, extra=1)

        if self.request.method == 'POST':
            context_data['formset'] = VersionFormset(self.request.POST)
        else:
            context_data['formset'] = VersionFormset()

        return context_data

    def form_valid(self, form):
        product = form.save()
        product.trader = self.request.user
        product.save()

        formset = self.get_context_data()['formset']
        self.object = form.save()

        if formset.is_valid():
            formset.instance = product
            formset.save()

        if form.is_valid():
            new_product = form.save()
            new_product.slug = slugify(new_product.name_product)
            new_product.save()

        return super().form_valid(form)


class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Product
    permission_required = 'main.view_product'

    def get_context_data(self,*args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        products = Product.objects.all()

        for product in products:
            version = Version.objects.filter(name_product=product)
            sign_current_version = version.filter(sign_current_version=True)

            if sign_current_version:
                product.name_version = sign_current_version.last().name_version
                product.version_number = sign_current_version.last().version_number

        context_data['object_list'] = products
        context_data['title'] = 'Главная'
        context_data['trader_group'] = self.request.user.groups.filter(name='trader')

        return context_data


class ProductDetailtView(LoginRequiredMixin, DetailView):
    model = Product


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        VersionFormset = inlineformset_factory(Product, Version, form=VersionForm, extra=1)

        if self.request.method == 'POST':
            context_data['formset'] = VersionFormset(self.request.POST, instance=self.object)
        else:
            context_data['formset'] = VersionFormset(instance=self.object)

        return context_data

    def test_func(self):
        if ((self.get_object().trader == self.request.user) or self.request.user.is_superuser or
                self.request.user.groups.filter(name='moderator')):
            return True

        else:
            return self.handle_no_permission()

    def get_form_class(self):
        if self.request.user.groups.filter(name='moderator') or self.request.user.is_superuser:

            return ModeratorFormProducts

        return ProductForm

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        self.object = form.save()

        if formset.is_valid():
            formset.instance = self.object
            formset.save()

        if form.is_valid():
            new_product = form.save()
            new_product.slug = slugify(new_product.name_product)
            new_product.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('main:view_product', args=[self.kwargs.get('pk')])


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('main:index')

    def test_func(self):

        return self.request.user.is_superuser


def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        print(f'{name} ({email})')
    return render(request, 'main/contacts.html')


class ContactPageView(LoginRequiredMixin, TemplateView):
    template_name = "main/contacts.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Контакты'

        return context_data
