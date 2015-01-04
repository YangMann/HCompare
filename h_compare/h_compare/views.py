__author__ = 't-yaz'

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template


def home(request):
    return render_to_response("index.html")
