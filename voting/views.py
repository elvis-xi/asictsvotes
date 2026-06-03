import csv
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .models import Student, Election, Candidate, Vote
from .forms import LoginForm, ElectionForm, CandidateForm
from .otp_utils import generate_otp, send_otp_email, store_otp, verify_otp, clear_otp

def is_admin(user):
    return user.is_staff or user.is_superuser

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Step 2: OTP verification
    if request.method == 'POST' and 'otp_code' in request.POST:
        otp_code = request.POST.get('otp_code')
        user_id = request.session.get('pending_otp_user_id')
        if user_id and verify_otp(user_id, otp_code):
            user = Student.objects.get(id=user_id)
            login(request, user)
            clear_otp(user_id)
            del request.session['pending_otp_user_id']
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid or expired OTP. Please login again.')
            return redirect('login')

    # Step 1: Credentials
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            matric_number = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=matric_number, password=password)
            if user is not None:
                if not user.email:
                    messages.error(request, 'No email registered. Contact admin.')
                    return redirect('login')
                otp = generate_otp()
                send_otp_email(user.email, otp)
                store_otp(user.id, otp)
                request.session['pending_otp_user_id'] = user.id
                request.session['otp_expiry'] = time.time() + 30
                return render(request, 'voting/otp_verify.html', {
                    'matric': matric_number,
                    'expiry': request.session['otp_expiry']
                })
        messages.error(request, 'Invalid matric number or password')
    else:
        form = LoginForm()

    return render(request, 'voting/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    elections = Election.objects.all()
    user_votes = Vote.objects.filter(user=request.user).values_list('election_id', flat=True)
    
    elections_data = []
    for election in elections:
        elections_data.append({
            'election': election,
            'has_voted': election.id in user_votes,
            'status': election.status,
        })
    
    return render(request, 'voting/dashboard.html', {
        'elections': elections_data,
        'user': request.user,
    })

@login_required
def voting_page(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    if election.status != 'active':
        messages.error(request, 'This election is not currently active')
        return redirect('dashboard')

    existing_vote = Vote.objects.filter(user=request.user, election=election).first()
    if existing_vote:
        messages.warning(request, 'You have already voted in this election')
        return redirect('results', election_id=election.id)

    # Faculty restriction check
    if election.allowed_faculty and election.allowed_faculty.strip():
        if not request.user.faculty or request.user.faculty != election.allowed_faculty:
            messages.error(request, f'This election is restricted to {election.allowed_faculty} faculty only.')
            return redirect('dashboard')

    candidates = Candidate.objects.filter(election=election)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)

        vote = Vote.objects.create(
            user=request.user,
            candidate=candidate,
            election=election
        )

        candidate.vote_count += 1
        candidate.save()

        messages.success(request, f'✓ Your vote has been cast for {candidate.name}!')
        return redirect('results', election_id=election.id)

    return render(request, 'voting/voting.html', {
        'election': election,
        'candidates': candidates,
    })

@login_required
def results_view(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election).order_by('-vote_count')
    total_votes = election.total_votes
    
    chart_data = {
        'labels': [c.name for c in candidates],
        'votes': [c.vote_count for c in candidates],
        'positions': [c.position for c in candidates],
    }
    
    has_voted = Vote.objects.filter(user=request.user, election=election).exists()
    
    return render(request, 'voting/results.html', {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes,
        'chart_data': chart_data,
        'has_voted': has_voted,
    })

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    elections = Election.objects.all()
    total_students = Student.objects.count()
    total_votes = Vote.objects.count()
    
    context = {
        'elections': elections,
        'total_students': total_students,
        'total_votes': total_votes,
        'active_elections': Election.objects.filter(is_active=True, end_time__gte=timezone.now()).count(),
    }
    return render(request, 'voting/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save()
            messages.success(request, f'Election "{election.title}" created successfully!')
            return redirect('admin_dashboard')
    else:
        form = ElectionForm()
    
    return render(request, 'voting/create_election.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def add_candidate(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            candidate.save()
            messages.success(request, f'Candidate "{candidate.name}" added successfully!')
            return redirect('admin_dashboard')
    else:
        form = CandidateForm()
    
    return render(request, 'voting/add_candidate.html', {
        'form': form,
        'election': election,
    })

@login_required
@user_passes_test(is_admin)
def toggle_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    election.is_active = not election.is_active
    election.save()
    status = 'activated' if election.is_active else 'deactivated'
    messages.success(request, f'Election "{election.title}" has been {status}.')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def bulk_import_students(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin_dashboard')
        
        decoded = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded)
        
        required = {'matric_number', 'full_name'}
        if not required.issubset(reader.fieldnames):
            messages.error(request, f'CSV must contain columns: {", ".join(required)}')
            return redirect('admin_dashboard')
        
        created = 0
        errors = []
        for row in reader:
            matric = row.get('matric_number', '').strip()
            name = row.get('full_name', '').strip()
            faculty = row.get('faculty', '').strip() or None
            email = row.get('email', '').strip() or None
            dept = row.get('department', '').strip() or ''
            
            if not matric or not name:
                errors.append(f'Missing data: {row}')
                continue
            if Student.objects.filter(matric_number=matric).exists():
                errors.append(f'Duplicate: {matric}')
                continue
            
            Student.objects.create(
                matric_number=matric,
                full_name=name,
                faculty=faculty,
                email=email,
                department=dept,
                password=make_password(matric),
                is_active=True
            )
            created += 1
        
        messages.success(request, f'{created} students added. Errors: {len(errors)}')
        if errors:
            messages.warning(request, f'First error: {errors[0]}')
        return redirect('admin_dashboard')
    
    return render(request, 'voting/bulk_import.html')

def election_time_left(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    now = timezone.now()
    
    if election.end_time > now:
        time_left = (election.end_time - now).total_seconds()
    else:
        time_left = 0
    
    return JsonResponse({
        'time_left': int(time_left),
        'status': election.status,
    })

def resend_otp(request):
    if request.method == 'POST':
        user_id = request.session.get('pending_otp_user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Session expired. Please login again.'})
        try:
            user = Student.objects.get(id=user_id)
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
        if not user.email:
            return JsonResponse({'success': False, 'message': 'No email registered.'})
        
        otp = generate_otp()
        send_otp_email(user.email, otp)
        store_otp(user.id, otp)
        new_expiry = time.time() + 30
        request.session['otp_expiry'] = new_expiry
        return JsonResponse({'success': True, 'expiry': new_expiry})
    return JsonResponse({'success': False, 'message': 'Invalid request'})