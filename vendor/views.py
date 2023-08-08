from django.db.utils import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from .models import Vendor
from .forms import VendorForm
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
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
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
        try:
            if form.is_valid():
                category = form.save(commit=False)
                category.vendor = get_vendor(request)
                category_name = form.cleaned_data['category_name']
                category.slug = slugify(category_name)+'-'+str(category.vendor.pk)
                form.save()
                messages.success(request, 'Category added successfully!')
                return redirect('menu_builder')
            else:
                print(form.errors)
        except IntegrityError:  # duplicate key value violates unique constraint "menu_fooditem_slug_key"
            messages.error(request, 'Category with this name already exists.')
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
    try:
        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                category = form.save(commit=False)
                category.vendor = get_vendor(request)
                category_name = form.cleaned_data['category_name']
                category.slug = slugify(category_name)+'-'+str(category.vendor.pk)
                form.save()
                messages.success(request, 'Category updated successfully!')
                return redirect('menu_builder')
            else:
                print(form.errors)
    except IntegrityError:  # duplicate key value violates unique constraint
        messages.error(request, 'Category with this name already exists.')
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
        try:
            if form.is_valid():
                food = form.save(commit=False)
                food.vendor = get_vendor(request)
                food_title = form.cleaned_data['food_title']
                food.slug = slugify(food_title)+'-'+str(food.vendor.pk)
                form.save()
                messages.success(request, 'Food Item added successfully!')
                return redirect('fooditems_by_category', food.category.pk)
            else:
                print(form.errors)
        except IntegrityError:  # duplicate key value violates unique constraint
            messages.error(request, 'Food item with this name already exists.')
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
        try:
            if form.is_valid():
                food = form.save(commit=False)
                food.vendor = get_vendor(request)
                food_title = form.cleaned_data['food_title']
                food.slug = slugify(food_title)+'-'+str(food.vendor.pk)
                form.save()
                messages.success(request, 'Food Item updated successfully!')
                return redirect('fooditems_by_category', food.category.pk)
            else:
                print(form.errors)
        except IntegrityError:  # duplicate key value violates unique constraint
            messages.error(request, 'Food item with this name already exists.')
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
