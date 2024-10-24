from django.urls import path
from . import views

urlpatterns = [

    path('',views.scrape_function,name="head_function"),
    path('inovation/',views.inovation,name="inovation"),
    path('business/',views.business,name="business"),
    path('culture/',views.culture,name="culture"),
    path('aboutus/',views.aboutus,name="aboutus"),
    path('news/',views.news,name="news"),
    path('arts/', views.arts, name="arts"),
]
