from django.shortcuts import render

from mainapp.models import Product, ProductCategory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page


def index(request):
    return render(request, 'mainapp/index.html', {'title': 'Главная'})


# def products(request, category_id=None):
#     context = {
#         'categories': ProductCategory.objects.all(),
#         'products': Product.objects.filter(category_id=category_id) if category_id else Product.objects.all(),
#     }
#     return render(request, 'mainapp/products.html', context)

def products(request, category_id=None, page=1):
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    per_page = 3
    paginator = Paginator(products.order_by('-price'), per_page)
    products_paginator = paginator.page(page)
    context = {'categories': ProductCategory.get_all(), 'products': products_paginator}
    return render(request, 'mainapp/products.html', context)
