from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
import re

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(regex.match(path) for regex in self.exempt_urls):
                return redirect(f'{reverse("login")}?next={request.path_info}')
        
        return self.get_response(request)
