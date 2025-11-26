from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Avg
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

class HomePageView(LoginRequiredMixin, ListView):
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


@login_required
def frontend_home(request):
    filterable_programs = [
        {
            'name': 'BS Information Technology',
            'logo_url': 'images/SITE-LOGO.jpg',
            'id': 'it',
        },
        {
            'name': 'BS Computer Science',
            'logo_url': 'images/ACS-LOGO.png',
            'id': 'cs',
        },
    ]

    active_program_name = request.GET.get('program') or None

    featured_theses = _build_thesis_queryset().order_by('-date_added')
    if active_program_name:
        featured_theses = featured_theses.filter(program__prog_name=active_program_name)

    featured_theses = featured_theses[:6]
    context = {
        'stats': _get_site_stats(),
        'featured_theses': featured_theses,
        'filterable_programs': filterable_programs,
        'active_program_name': active_program_name,
    }
    return render(request, 'home.html', context)


@login_required
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

    user_uploads = []
    if request.user.is_authenticated and not query:
        user_uploads = _build_thesis_queryset().filter(uploaded_by=request.user).order_by('-date_added')

    context = {
        'page_obj': page_obj,
        'query': query,
        'user_uploads': user_uploads,
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
    total_views_data = uploads.aggregate(total_views=Sum('view_count'))
    total_views = total_views_data['total_views'] or 0
    average_score_data = uploads.filter(panel_score__isnull=False).aggregate(average_score=Avg('panel_score'))
    average_score = average_score_data['average_score']
    context = {
        'uploads': uploads,
        'stats': _get_site_stats(),
        'total_views': total_views,
        'average_score': average_score,
    }
    return render(request, 'profile.html', context)


@login_required
def thesis_detail(request, pk):
    thesis = get_object_or_404(_build_thesis_queryset(), pk=pk)
    Thesis.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    thesis.refresh_from_db()
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
