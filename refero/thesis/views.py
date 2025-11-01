from django.shortcuts import render
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from thesis.models import Thesis, Program, College, Tag

class SignUpView(CreateView):
    form_class = UserCreationForm
    #template_name = "account/register.html"  # your template path
    success_url = reverse_lazy('account_login')  

class HomePageView(ListView):
    model = Thesis
    context_object_name = 'base'
    template_name = "base.html"
    paginate_by = 3 


# Create your views here.
