from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TaskForm
from .models import Task


def home(request):
    return render(request, 'home.html', {
        'form': TaskForm(),
        'tasks': Task.objects.all(),
    })


@require_POST
def add_task(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'home.html', {
        'form': form,
        'tasks': Task.objects.all(),
    }, status=400)


@require_POST
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save(update_fields=['completed'])
    return redirect('home')


@require_POST
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('home')


def about(request):
    context = {'myname': 'Justin'}
    return render(request, 'about.html', context)