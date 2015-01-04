__author__ = 't-yaz'

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template

from h_compare.core import HCompare


def home(request):
    return render_to_response("index.html", context_instance=RequestContext(request))


def compare(request):
    if request.META.get('REQUEST_METHOD', 'UNKNOWN') == 'POST':
        h_compare = HCompare(request.POST.get('url_1'), request.POST.get('url_2'))
        c = RequestContext(request, {"result": h_compare.compare()})
        t = get_template('result.html')
        return HttpResponse(t.render(c))
    else:
        c = RequestContext(request)
        t = get_template('index.html')
        return HttpResponse(t.render(c))