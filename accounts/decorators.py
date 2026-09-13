from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def _exige(login_url, autorise, message):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url)
            if not autorise(request.user):
                messages.error(request, message)
                return redirect(login_url)
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


admin_requis = _exige(
    'accounts:login_admin',
    lambda user: user.est_admin,
    'Cet espace est reserve aux administrateurs.',
)

conseiller_requis = _exige(
    'accounts:login_conseiller',
    lambda user: user.est_conseiller,
    'Cet espace est reserve aux conseillers.',
)
