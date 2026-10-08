from django.contrib import admin
from django.urls import path
from todo_list import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:pk>/toggle/', views.toggle_task, name='toggle_task'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('about/', views.about, name='about'),
]