# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse
from django.core.context_processors import csrf

def json_response(data, request):
    response = HttpResponse(json.dumps(data), content_type='application/json')
    response.set_cookie('csrftoken', unicode(csrf(request)['csrf_token']))
    return response

