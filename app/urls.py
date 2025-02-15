from django.urls import path,include
from .import views

urlpatterns = [
     path('', views.home, name='home'),
     path('download/<int:naat_id>/', views.download_page, name='download_page'),
     path('download_audio/<int:naat_id>/', views.download_audio, name='download_audio'),
     path('search/', views.search_naats, name='search'),

    
]
