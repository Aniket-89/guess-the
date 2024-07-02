# views.py
import datetime
import random
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from .forms import ChatForm
from .gemini import generateFacts

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi",
    "Puducherry", "Jammu and Kashmir", "Ladakh"
]
# TODAYS_STATE = ""  #changes every 12am

state_facts = []
def get_todays_facts():
    current_date = datetime.now().date()
    facts_cache_key = f"facts_{current_date}"
    state_cache_key = f"state_{current_date}"
    state = cache.get(state_cache_key)
    facts = cache.get(facts_cache_key)
    if not state:
        state = random.choice(STATES)
        cache.set(state_cache_key, state, timeout=24*60*60)  # Cache for 24 hours

    if not facts:
        # global TODAYS_STATE
        # TODAYS_STATE = random.choice(STATES)
        
        facts = generateFacts(state)
        cache.set(facts_cache_key, facts, timeout=24*60*60)  # Cache for 24 hours

    return facts, state


def index_view(request):
    hints, state = get_todays_facts()
    
    form = ChatForm()
    message = ""
    last_attempt_time = request.session.get('last_attempt_time')
    attempts = 0
    if last_attempt_time:
        show_hints = hints
        last_attempt_time = timezone.datetime.fromisoformat(last_attempt_time)
        if timezone.now() - last_attempt_time < timedelta(days=1):
            message = "You have already attempted today. Please try again tomorrow."

    context = {
        'form': form,
        'state': state,
        'message': message,
        'show_hints': show_hints,
        'attempts': attempts,
    }
    return render(request, 'core/index.html', context)

def check_guess(request):
    
    incorrect_attempts = request.session.get('incorrect_attempts', 0)
    show_hints = []
    message = ""

    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            user_choice = form.cleaned_data["select_field"]
            if user_choice != TODAYS_STATE:
                incorrect_attempts += 1
                request.session['incorrect_attempts'] = incorrect_attempts
                hints = get_todays_facts()
                show_hints = hints[:incorrect_attempts]
                if incorrect_attempts >= 5:
                    message = "You failed! The correct state was {}.".format(TODAYS_STATE)
                    request.session['incorrect_attempts'] = 0  # Reset attempts after failure
            else:
                message = "You guessed correct!"
                request.session['incorrect_attempts'] = 0  # Reset on correct guess
            request.session['last_attempt_time'] = timezone.now().isoformat()
        else:
            show_hints = hints[:incorrect_attempts]

        context = {
            'form': form,
            'show_hints': show_hints,
            'message': message,
            'attempts': incorrect_attempts
        }

        return render(request, 'core/index.html', context)
    else:
        return redirect('index')
