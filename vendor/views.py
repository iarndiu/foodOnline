from django.shortcuts import render
from .models import Vendor

# Create your views here.


def v_profile(request):
    return render(request, 'vendor/v_profile.html')
