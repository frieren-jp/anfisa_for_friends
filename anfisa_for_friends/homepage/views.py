from django.shortcuts import render
from ice_cream.models import IceCream


def index(request):
    template = 'homepage/index.html'
    context = {'ice_cream_list': IceCream.objects.filter(
        is_published=True, is_on_main=True, category__is_published=True,
    ).order_by('category__output_order', 'title')}
    return render(request, template, context)
