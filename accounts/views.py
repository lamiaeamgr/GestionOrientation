from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    ConnexionAdminForm,
    ConnexionCandidatForm,
    ConnexionConseillerForm,
    InscriptionForm,
)


class ConnexionView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = ConnexionCandidatForm
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy('dashboard:candidat')


class ConnexionAdminView(LoginView):
    template_name = 'accounts/login_admin.html'
    authentication_form = ConnexionAdminForm

    def get_success_url(self):
        return reverse_lazy('administration:accueil')


class ConnexionConseillerView(LoginView):
    template_name = 'accounts/login_conseiller.html'
    authentication_form = ConnexionConseillerForm

    def get_success_url(self):
        return reverse_lazy('conseil:espace')


class DeconnexionView(LogoutView):
    next_page = reverse_lazy('accounts:login')


class DeconnexionAdminView(LogoutView):
    next_page = reverse_lazy('accounts:login_admin')


class DeconnexionConseillerView(LogoutView):
    next_page = reverse_lazy('accounts:login_conseiller')


def inscription(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Votre compte a ete cree. Completez maintenant votre dossier academique.',
            )
            return redirect('candidats:profil')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/register.html', {'form': form})
