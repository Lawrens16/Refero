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

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import requests

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            code = str(random.randint(100000, 999999))
            request.session['reset_code'] = code
            request.session['reset_email'] = email
            
            send_mail(
                'Password Reset Verification Code',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('password_reset_verify')
        else:
            messages.error(request, "Email not found.")
    return render(request, 'registration/password_reset_form.html')

def password_reset_verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        session_code = request.session.get('reset_code')
        if code == session_code:
            request.session['reset_verified'] = True
            return redirect('password_reset_confirm_custom')
        else:
            messages.error(request, "Invalid code.")
    return render(request, 'registration/password_reset_verify_code.html')

def password_reset_confirm_custom(request):
    if not request.session.get('reset_verified'):
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        p1 = request.POST.get('password_1')
        p2 = request.POST.get('password_2')
        if p1 == p2:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(p1)
            user.save()
            # Clean up session
            del request.session['reset_code']
            del request.session['reset_email']
            del request.session['reset_verified']
            return redirect('password_reset_complete')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'registration/password_reset_confirm.html')

class SignUpView(CreateView):
    form_class = UserCreationForm
    #template_name = "account/register.html"  # your template path
    success_url = reverse_lazy('account_login')  

class HomePageView(LoginRequiredMixin, ListView):
    model = Thesis
    context_object_name = 'base'
    template_name = "base.html"
    paginate_by = 3 


SS_API_BASE_URL = "https://api.semanticscholar.org/graph/v1"
SS_RECOMMENDATIONS_URL = "https://api.semanticscholar.org/recommendations/v1/papers/forpaper/"

def get_paper_id(title: str) -> str | None:
    """Uses the /paper/search endpoint to find a paper's unique ID."""
    search_url = f"{SS_API_BASE_URL}/paper/search"
    
    headers = {
        'x-api-key': settings.SEMANTIC_SCHOLAR_CONFIG.get("API_KEY"),
        'Content-Type': 'application/json'
    }
    
    params = {
        'query': title,
        'fields': 'paperId',
        'limit': 1 
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if results exist and return the first paperId
        if data.get('data') and len(data['data']) > 0:
            return data['data'][0].get('paperId')
        
    except requests.exceptions.RequestException as e:
        print(f"Error during Semantic Scholar ID lookup for '{title}': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during ID lookup: {e}")
        return None
    return None

def get_thesis_recommendations(thesis_title: str, ss_paper_id: str = None) -> list:
    """
    Fetches related paper recommendations using a two-step process: lookup and recommendation.
    Uses stored ss_paper_id if available, otherwise looks it up by title.
    """
    paper_id = ss_paper_id
    
    if not paper_id:
        paper_id = get_paper_id(thesis_title)
    
    if not paper_id:
        print(f"No Semantic Scholar ID found for: {thesis_title}")
        return []

    recommendations_url = f"{SS_RECOMMENDATIONS_URL}{paper_id}"
    
    headers = {
        'x-api-key': settings.SEMANTIC_SCHOLAR_CONFIG.get("API_KEY"),
        'Content-Type': 'application/json'
    }

    params = {
        'fields': 'title,authors.name,year,abstract',
        'limit': 5
    }

    try:
        response = requests.get(recommendations_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # The recommendations endpoint returns a list of papers under 'recommendedPapers'
        return data.get('recommendedPapers', [])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching recommendations for ID {paper_id}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during recommendation fetch: {e}")
        return []


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
    tag_filter = request.GET.get('tag', '').strip()
    base_qs = _build_thesis_queryset().order_by('-date_added')

    if query:
        base_qs = base_qs.filter(
            Q(title__icontains=query)
            | Q(authors__icontains=query)
            | Q(abstract__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()

    if tag_filter:
        base_qs = base_qs.filter(tags__name__iexact=tag_filter)

    paginator = Paginator(base_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_uploads = []
    if request.user.is_authenticated and not query:
        user_uploads = _build_thesis_queryset().filter(uploaded_by=request.user).order_by('-date_added')

    context = {
        'page_obj': page_obj,
        'query': query,
        'tag_filter': tag_filter,
        'available_tags': Tag.objects.order_by('name')[:30],
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

            # Part 2: Integrate Lookup into the Creation Logic
            ss_id = get_paper_id(thesis.title)
            if ss_id:
                thesis.ss_paper_id = ss_id
                thesis.save()

            messages.success(request, 'Thesis uploaded successfully.')
            return redirect('theses')
    else:
        form = ThesisUploadForm()

    return render(request, 'thesis_upload.html', {
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
    
    recommendations = get_thesis_recommendations(thesis.title, thesis.ss_paper_id)
    
    context = {
        'thesis': thesis,
        'stats': _get_site_stats(),
        'recommendations': recommendations,
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
