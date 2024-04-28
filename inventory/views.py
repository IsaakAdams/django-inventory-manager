from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.http import HttpRequest
from .forms import UserRegisterForm, InventoryItemForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import InventoryItem, Category
from inventory_manager.settings import LOW_QUANTITY
from django.contrib import messages

class Index(TemplateView):
    template_name = 'inventory/index.html'


class Dashboard(LoginRequiredMixin, View):
    def get(self, request:HttpRequest):
        # Get all the items in the database
        items = InventoryItem.objects.filter(user=self.request.user.id).order_by('id')

        low_inventory = InventoryItem.objects.filter(
            user = self.request.user.id,
            # Check weather inventory item's quantity is 
            # (lte)-Less than or equal to the LOW_QUANTITY variable set in settings.py
            quantity__lte=LOW_QUANTITY
        )

        if low_inventory.count() > 0:
            if low_inventory.count() > 1:
                messages.error(request, f'{low_inventory.count()} items have low inventory')
            else:
                messages.error(request, f'{low_inventory.count()} item has low inventory')
        
        low_inventory_ids = InventoryItem.objects.filter(
            user = self.request.user.id,
            quantity__lte=LOW_QUANTITY
        ).values_list('id', flat=True)

        context = {
            'items': items,
            'low_inventory_ids': low_inventory_ids,
        }

        return render(request, 'inventory/dashboard.html', context)


class SignUpView(View):
    def get(self, request: HttpRequest):
        # Creating empty User Form for User to fill out
        form = UserRegisterForm()

        # Creating a context to be returned to the signup.html page
        context = {
            'error': None,
            'form': form
        }

        # Render signup.html page
        return render(request, 'inventory/signup.html', context)


    def post(self, request: HttpRequest):
        # Create an instance of the User form with all the data filled in
        # Data will be sent via POST request on signup.html page

        form = UserRegisterForm(request.POST)

        # if the form has no errors
        # Authenticate the new user using the data that they passed in
        # and log in.
        # Send them back to the home page
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )

            login(request, user)

            return redirect('index')
        else:
            # Form was invalid
            # Send user back to the signup page with an error displayed

            context = {
                'form': form,
            }
            return render(request, 'inventory/signup.html', context)


class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')

    # Get Category data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditItem(LoginRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('dashboard')


class DeleteItem(LoginRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/delete_item.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'item'