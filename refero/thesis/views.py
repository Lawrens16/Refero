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
    template_name = "dashboard.html"
    paginate_by = 3 


# Create your views here.

def frontend_home(request):
    return render(request, "home.html")


def frontend_theses(request):
    return render(request, "theses.html")


def frontend_upload(request):
    return render(request, "upload.html")


def frontend_profile(request):
    return render(request, "profile.html")

def frontend_dashboard(request):
    return render(request, "dashboard.html")