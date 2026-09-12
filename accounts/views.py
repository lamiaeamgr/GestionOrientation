from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import InscriptionForm


class ConnexionView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('dashboard:home')


def inscription(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Votre compte a ete cree. Completez maintenant votre dossier academique.')
            return redirect('candidats:profil')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/register.html', {'form': form})
