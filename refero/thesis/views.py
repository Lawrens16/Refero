from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from thesis.forms import ThesisUploadForm
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



def _build_thesis_queryset():
    """Reusable queryset with the relations we always display."""
    return Thesis.objects.select_related('college', 'program').prefetch_related('tags')


def _get_site_stats():
    return {
        'thesis_count': Thesis.objects.count(),
        'college_count': College.objects.count(),
        'program_count': Program.objects.count(),
        'tag_count': Tag.objects.count(),
    }


def frontend_home(request):
    featured_theses = _build_thesis_queryset().order_by('-date_added')[:6]
    context = {
        'stats': _get_site_stats(),
        'featured_theses': featured_theses,
    }
    return render(request, 'home.html', context)


def frontend_theses(request):
    query = request.GET.get('q', '').strip()
    base_qs = _build_thesis_queryset().order_by('-date_added')

    if query:
        base_qs = base_qs.filter(
            Q(title__icontains=query)
            | Q(authors__icontains=query)
            | Q(abstract__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()

    paginator = Paginator(base_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'stats': _get_site_stats(),
    }
    return render(request, 'theses.html', context)


@login_required
def frontend_upload(request):
    if request.method == 'POST':
        form = ThesisUploadForm(request.POST, request.FILES)
        if form.is_valid():
            thesis = form.save(commit=False)
            thesis.uploaded_by = request.user
            thesis.save()
            form.save_m2m()
            messages.success(request, 'Thesis uploaded successfully.')
            return redirect('theses')
    else:
        form = ThesisUploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'stats': _get_site_stats(),
    })


@login_required
def frontend_profile(request):
    uploads = _build_thesis_queryset().filter(uploaded_by=request.user).order_by('-date_added')
    context = {
        'uploads': uploads,
        'stats': _get_site_stats(),
    }
    return render(request, 'profile.html', context)


def thesis_detail(request, pk):
    thesis = get_object_or_404(_build_thesis_queryset(), pk=pk)
    context = {
        'thesis': thesis,
        'stats': _get_site_stats(),
    }
    return render(request, 'thesis_detail.html', context)


@login_required
def thesis_edit(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    if thesis.uploaded_by != request.user:
        return HttpResponseForbidden("You do not have permission to edit this thesis.")

    if request.method == 'POST':
        form = ThesisUploadForm(request.POST, request.FILES, instance=thesis)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thesis updated successfully.')
            return redirect('profile')
    else:
        form = ThesisUploadForm(instance=thesis)

    return render(request, 'thesis_edit.html', {
        'form': form,
        'thesis': thesis,
        'stats': _get_site_stats(),
    })


@login_required
def thesis_delete(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    if thesis.uploaded_by != request.user:
        return HttpResponseForbidden("You do not have permission to delete this thesis.")

    if request.method == 'POST':
        thesis.delete()
        messages.success(request, 'Thesis deleted successfully.')
        return redirect('profile')

    return render(request, 'thesis_confirm_delete.html', {
        'thesis': thesis,
        'stats': _get_site_stats(),
    })
