
from django.contrib import admin
from django.urls import path
from django.urls import include
#from speakeasyApp import views  #speakeasyApp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('speakeasyApp.urls')),
    


]
