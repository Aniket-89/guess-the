# views.py
import datetime
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from .forms import ChatForm
from .gemini import generateFacts

TODAYS_STATE = "Kerala"  #changes every 12am

state_facts = []
def get_todays_facts():
    current_date = datetime.now().date()
    facts_cache_key = f"facts_{current_date}"

    facts = cache.get(facts_cache_key)
    if not facts:
        facts = generateFacts(TODAYS_STATE)
        cache.set(facts_cache_key, facts, timeout=24*60*60)  # Cache for 24 hours

    return facts
def index_view(request):
    form = ChatForm()
    message = ""
    last_attempt_time = request.session.get('last_attempt_time')

    if last_attempt_time:
        last_attempt_time = timezone.datetime.fromisoformat(last_attempt_time)
        if timezone.now() - last_attempt_time < timedelta(days=1):
            message = "You have already attempted today. Please try again tomorrow."

    context = {
        'form': form,
        'message': message
    }
    return render(request, 'core/index.html', context)

def check_guess(request):
    # hints = [
    #     "Hint 1: Lorem ipsum, dolor sit amet consectetur adipisicing elit.",
    #     "Hint 2: Lorem ipsum, dolor sit amet consectetur adipisicing elit.",
    #     "Hint 3: Lorem ipsum, dolor sit amet consectetur adipisicing elit.",
    #     "Hint 4: Lorem ipsum, dolor sit amet consectetur adipisicing elit.",
    #     "Hint 5: Lorem ipsum, dolor sit amet consectetur adipisicing elit.",
    # ]
    
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
        }

        return render(request, 'core/index.html', context)
    else:
        return redirect('index')
