from django.shortcuts import get_object_or_404, render

from .models import IceCream


def ice_cream_detail(request, pk):
    template = 'ice_cream/detail.html'
    context = {'ice_cream': get_object_or_404(
        IceCream.objects.filter(is_published=True, category__is_published=True),
        pk=pk,
    )}
    return render(request, template, context)


def ice_cream_list(request):
    template = 'ice_cream/list.html'
    context = {'ice_cream_list': IceCream.objects.filter(
        is_published=True, category__is_published=True,
    ).select_related('category').order_by('category__output_order', 'title')}
    return render(request, template, context)
