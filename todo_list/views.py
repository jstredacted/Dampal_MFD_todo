from datetime import datetime
from django.shortcuts import render

def home(request):
    now = datetime.now()
    date_str = now.strftime('%B %d %Y')
    context = {"date_today": date_str}
    return render(request, 'home.html', context)

def about(request):
    context = {'myname': 'Justin'}
    return render(request, 'about.html', context)