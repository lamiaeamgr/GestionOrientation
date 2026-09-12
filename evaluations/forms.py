from django import forms


class VerificationEmailForm(forms.Form):
    email = forms.EmailField(
        label='Votre adresse email ENSI',
        help_text=(
            "Utilisee uniquement pour verifier votre eligibilite. "
            "Elle n'est jamais stockee ni associee a vos reponses."
        ),
        widget=forms.EmailInput(attrs={'placeholder': 'prenom.nom@ensi-uma.tn'}),
    )
