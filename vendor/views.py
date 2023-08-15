from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import Vendor, OpeningHour
from .forms import VendorForm, OpeningHourForm
from menu.forms import CategoryForm, FoodItemForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from menu.models import Category, FoodItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from django.template.defaultfilters import slugify

# Create your views here.


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def v_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('v_profile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/v_profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category).order_by('created_at')
    context = {
        'vendor': vendor,
        'category': category,
        'fooditems': fooditems,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category_name = form.cleaned_data['category_name']
            category.save()
            category.slug = slugify(category_name)+'-'+str(category.pk)
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category_name = form.cleaned_data['category_name']
            category.save()
            category.slug = slugify(category_name)+'-'+str(category.pk)
            category.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
        'category': category,
        'form': form,
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food_title = form.cleaned_data['food_title']
            food.save()
            food.slug = slugify(food_title)+'-'+str(food.pk)
            food.save()
            messages.success(request, 'Food Item added successfully!')
            return redirect('fooditems_by_category', food.category.pk)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food_title = form.cleaned_data['food_title']
            food.save()
            food.slug = slugify(food_title)+'-'+str(food.pk)
            food.save()
            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_category', food.category.pk)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'food': food,
        'form': form,
    }
    return render(request, 'vendor/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Item has been deleted successfully!')
    return redirect('fooditems_by_category', food.category.pk)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day,
                                                  from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(pk=hour.pk)
                    if day.is_closed:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Opening hour has been added',
                            'pk': day.pk,
                            'day': day.get_day_display(),
                            'is_closed': 'Closed',
                        })
                    else:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Opening hour has been added',
                            'pk': day.pk,
                            'day': day.get_day_display(),
                            'from_hour': day.from_hour,
                            'to_hour': day.to_hour,
                        })
            except IntegrityError as e:
                return JsonResponse({
                    'status': 'failed',
                    'message': from_hour+'-'+to_hour+' already exists for this day',
                    'error': str(e),
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })


def remove_opening_hours(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                hour = get_object_or_404(OpeningHour, pk=pk)
                hour.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Opening hour has been deleted',
                    'pk': pk,
                })
            except:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Opening hour does not exist'
                })
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid request'
            })
