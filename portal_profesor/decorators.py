from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def profesor_required(view_func):
    """Exige estar logueado y tener un Profesor vinculado a la cuenta.
    Si un admin entra sin ser profesor, lo manda de vuelta al login
    (ajustar el redirect si querés una página de 'no autorizado' distinta)."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "profesor"):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    return wrapper
