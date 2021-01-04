from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            group = request.user.groups.all()
            group = str(group[0])
        except:
            group = None
        if group != 'Management' and request.user.is_authenticated:
            return redirect('feed')
        else:
            return view_func(request,
                             *args, **kwargs)

    return wrapper_func


def allowed_users(allowed=[]):
    def decorator(view_func):

        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == None:
                    return HttpResponse('Page access denied!!!')
                if group in allowed:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse('Page access denied!!!')
            else:
                return HttpResponse('Page access denied!!!')
        return wrapper_func
    return decorator
