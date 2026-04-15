import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Voter, Candidate, Election, Vote
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
current_time = timezone.localtime()
from django.utils.timezone import now
current_time = now()
from django.db.models import Sum, Count, Q
from .models import ElectionLog, Election
import random

# Simulate OTP sending
def send_otp(phone):
    return "123456"  # Simulated OTP

# =========================
# 🔐 ADMIN LOGIN
# =========================
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, "admin_login.html", {"error": "Invalid credentials"})

    return render(request, "admin_login.html")


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@login_required(login_url='admin_login')
def admin_dashboard(request):
    update_election_status()
    election = Election.objects.filter(is_active=True).first()
    return render(request, "admin_dashboard.html", {"election": election})


# =========================
# 📤 UPLOAD VOTERS
# =========================
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Voter

def upload_voters(request):
    if request.method == "POST" and request.FILES.get("file"):

        file = request.FILES["file"]

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        success = 0
        failed = 0
        valid_rows = []
        invalid_rows = []

        for row in reader:
            try:
                aadhaar = str(row["aadhaar_number"]).replace(".0", "")

                if "E" in aadhaar:
                    aadhaar = format(float(aadhaar), '.0f')

                voter, created = Voter.objects.get_or_create(
                    epic_number=row["epic_number"],   # 🔑 unique key

                    defaults={
                        "name": row["name"],
                        "aadhaar_number": aadhaar,
                        "phone": row["phone"],
                    "constituency": row["constituency"]
                    }
                )

                if created:
                    success += 1
                    valid_rows.append(voter)
                else:
                    # already exists → treat as failed or skip
                    failed += 1

            except Exception as e:
                print("ERROR:", e)
                invalid_rows.append(row)
                failed += 1

        return render(request, "voter_success.html", {
            "success": success,
            "failed": failed,
            "valid_rows": Voter.objects.all(),   # ✅ ALL voters in DB   # ✅ ALL voters in DB     # ✅ IMPORTANT
            "invalid_rows": invalid_rows  # ✅ IMPORTANT
        })

    return render(request, "upload_voters.html")

# =========================
# 📊 SUCCESS PAGE
# =========================
def voter_success(request):
    voters = Voter.objects.all()

    return render(request, 'voter_success.html', {
        'success_count': voters.count(),
        'failed_count': 0,
        'valid_rows': voters,   # 👈 DB data
        'invalid_rows': []
    })


# =========================
# 🏠 BASIC PAGES
# =========================
def home(request):
    return render(request, "index.html")


def user_login(request):
    return render(request, "login.html")


# =========================
# 🏠 MANAGE CANDIDATES
# =========================
def manage_candidates(request):
    if request.method == "POST":
        name = request.POST.get("name")
        party = request.POST.get("party").strip().lower()
        constituency = request.POST.get("constituency")

        symbol_map = {
            "congress": "symbols/congress.png",
            "bjp": "symbols/bjp.png",
            "trs": "symbols/trs.png",
            "tdp": "symbols/tdp.png",
        }

        symbol = symbol_map.get(party, None)

        Candidate.objects.create(
            name=name,
            party=party,
            constituency=constituency,
            symbol=symbol
        )

        return redirect("admin_dashboard")

    candidates = Candidate.objects.all()
    return render(request, "manage_candidates.html", {"candidates": candidates})


def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    messages.success(request, "Candidate deleted successfully!")
    return redirect("manage_candidates")


from django.shortcuts import render

@login_required(login_url='admin_login')
def start_stop_election(request):
    if request.method == "POST":
        name = request.POST.get("name")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        election, created = Election.objects.get_or_create(is_active=True)
        election.name = name
        election.start_time = start_time
        election.end_time = end_time
        election.is_active = True
        election.save()

        messages.success(request, "Election started successfully!")
        return redirect("admin_dashboard")

    return render(request, "start_stop_election.html")

@login_required(login_url='admin_login')

def view_results(request):
    election = Election.objects.filter(is_active=True).first()

    now = timezone.localtime()

    if election and election.end_time and now <= election.end_time:
        return render(request, "results.html", {
            "message": "Results will be available after election ends"
        })

    candidates = Candidate.objects.all().annotate(vote_count=Count('vote'))

    max_votes = max([c.vote_count for c in candidates]) if candidates else 0
    top_candidates = [c for c in candidates if c.vote_count == max_votes]

    if max_votes == 0:
        winner = "No votes yet"
    elif len(top_candidates) > 1:
        winner = "Draw"
    else:
        winner = top_candidates[0].name

    return render(request, 'results.html', {
        'results': candidates,
        'winner': winner
    })

@login_required(login_url='admin_login')
def logs(request):
    current_time = timezone.localtime()

    # 🟢 ACTIVE
    active_election = Election.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()

    # ⏳ SCHEDULED
    scheduled_elections = Election.objects.filter(
        start_time__gt=current_time
    )

    # ✅ COMPLETED
    completed_elections = Election.objects.filter(
        end_time__lt=current_time
    )

    context = {
        'active_election': active_election,
        'scheduled_elections': scheduled_elections,
        'completed_logs': completed_elections,
        'total_elections': Election.objects.count(),
        'active_count': 1 if active_election else 0,
        'scheduled_count': scheduled_elections.count(),
        'completed_count': completed_elections.count(),
    }

    return render(request, "logs.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Voter, Vote, Candidate, ElectionLog, Election

def system_settings(request):
    if request.method == "POST":
        if "reset_election" in request.POST:
            
            # 🔥 DELETE EVERYTHING
            Vote.objects.all().delete()          # votes
            Voter.objects.all().delete()         # voters
            ElectionLog.objects.all().delete()   # logs
            
            # optional (if you want full reset)
            Candidate.objects.all().delete()

            # reset election status
            Election.objects.all().update(is_active=False)

            messages.success(request, "🚀 Election reset successfully!")

        return redirect("system_settings")

    return render(request, "system_settings.html")

def update_election_status():
    now = timezone.localtime()

    elections = Election.objects.all()

    for election in elections:

        # Skip broken data safely
        if not election.start_time or not election.end_time:
            election.is_active = False
            election.save()
            continue

        if election.start_time <= now <= election.end_time:
            election.is_active = True
        else:
            election.is_active = False

        election.save()

# Step 1: Voter Authentication
import random

def voter_authentication(request):
    if request.method == "POST":
        epic = request.POST.get('epic')
        aadhaar = request.POST.get('aadhaar')

        try:
            voter = Voter.objects.get(
                epic_number=epic,
                aadhaar_number=aadhaar
            )

            # Store voter in session
            request.session['voter_id'] = voter.id

            # 🚫 Already voted check
            if voter.has_voted:
                return render(request, 'login.html', {
                'error': 'You have already voted!'
            })

            # 🔐 Generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp

            print("OTP:", otp)  # for testing

            return redirect('verify_otp')

        except Voter.DoesNotExist:
            return render(request, 'login.html', {
            'error': 'Invalid EPIC or Aadhaar'
        })

    # 🔥 IMPORTANT: always return login.html
    return render(request, 'login.html')

# Step 2: OTP Verification
def verify_otp(request):

    if not request.session.get('otp'):
        return redirect('login')  # 🔒 direct access block

    if request.method == "POST":

        entered_otp = ''.join([
            request.POST.get('otp1', '').strip(),
            request.POST.get('otp2', '').strip(),
            request.POST.get('otp3', '').strip(),
            request.POST.get('otp4', '').strip(),
            request.POST.get('otp5', '').strip(),
            request.POST.get('otp6', '').strip(),
        ])

        original_otp = request.session.get('otp')

        print("Entered OTP:", entered_otp)
        print("Session OTP:", original_otp)

        if len(entered_otp) != 6:
            messages.error(request, "Enter complete OTP.")
            return render(request, 'otp_verification.html')

        if entered_otp == original_otp:
            request.session.pop('otp', None)

            # 🔥 ADD THIS FLAG
            request.session['otp_verified'] = True

            return redirect('face_verification')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'otp_verification.html')

def face_verification(request):

    if not request.session.get('otp_verified'):
        return redirect('login')  # 🔒 block direct access

    if request.method == "POST":

        # 🔥 mark face verified
        request.session['face_verified'] = True

        return redirect('voting_page')

    return render(request, 'face_verification.html')

# Step 4: Voting Page
import uuid

from django.utils.timezone import now

def voting_page(request):

    voter_id = request.session.get('voter_id')
    face_verified = request.session.get('face_verified')

    if not voter_id or not face_verified:
        return redirect('login')

    voter = Voter.objects.get(id=voter_id)

    # 🔐 Prevent multiple votes
    if voter.has_voted:
        return redirect('vote_success')

    if request.method == "POST":
        candidate_id = request.POST.get('candidate_id')
        candidate = Candidate.objects.get(id=candidate_id)

        vote = Vote.objects.create(voter=voter, candidate=candidate)

        voter.has_voted = True
        voter.save()

        vote_id = str(uuid.uuid4())[:8].upper()

        request.session['vote_id'] = vote_id
        request.session['vote_time'] = now().strftime("%d %b %Y, %I:%M %p")

        return redirect('vote_success')

    candidates = Candidate.objects.all()
    return render(request, 'voting_page.html', {'candidates': candidates})

from django.utils.timezone import localtime

def vote_success(request):
    voter_id = request.session.get('voter_id')

    vote = Vote.objects.get(voter_id=voter_id)

    vote_time = localtime(vote.created_at).strftime("%d %b %Y, %I:%M %p")

    return render(request, 'vote_success.html', {
        'vote_id': request.session.get('vote_id'),
        'vote_time': vote_time
    })