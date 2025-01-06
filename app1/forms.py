from datetime import timedelta
from django.utils import timezone
import re
from django import forms

def validate_text(value):
    if value and (not value.isalpha() or value[0].islower()):
        raise forms.ValidationError("Câmpurile trebuie să conțină doar litere si sa inceapa cu litrea mare")
        
def isPositive(x):
    if x < 0:
        raise forms.ValidationError("Valoarea trebuie sa fie pozitiva")
    
def hasLink(x):
    if (not x.startswith("https://")) and (not x.startswith("http://")):
        raise forms.ValidationError("Trebuie sa aiba un link")
    
def checkIntegerInRange(x, Min, Max):
    if x < Min or x > Max:
        raise forms.ValidationError("Valoarea trebuie sa fie intre " + str(Min) + " si " + str(Max))

from .models import Film, Cinematograf
from datetime import time

class BileteForm(forms.Form):
    cinema = forms.ChoiceField(
        choices=[(cinema.oras, cinema.oras) for cinema in Cinematograf.objects.all()],
        label='Cinema',
        required=True
    )
    nume = forms.ChoiceField(
        choices=[(None, '----')] + [(film.titlu, film.titlu) for film in Film.objects.all()], 
        label='Nume', 
        required=False
    )
    ora_inceput = forms.TimeField(
        label='Incepe dupa ora', 
        widget = forms.TimeInput(format='%H:%M'), 
        required=False
    )
    THREE_D_CHOICES = [
        ('both', 'Ambele'),
        (True, 'Da'),
        (False, 'Nu'),
    ]
    este_3D = forms.ChoiceField(label='Este 3D', choices=THREE_D_CHOICES, required=False)
    
    def clean_ora_inceput(self):
        ora_inceput = self.cleaned_data['ora_inceput']
        # check if input has been given
        if not ora_inceput:
            ora_inceput = time(8, 0)
        
        start_time = time(8, 0)
        end_time = time(14, 0)
        
        # start time of film must be between 8:00 AM and 2:00 PM
        if not (start_time <= ora_inceput <= end_time):
            raise forms.ValidationError("Ora trebuie să fie între 8:00 și 14:00.")
        return ora_inceput

class ContactForm(forms.Form):
    nume = forms.CharField(label='Nume', max_length=10, required=True, validators=[validate_text])
    prenume = forms.CharField(label='Prenume', required=False, validators=[validate_text])
    data_nasterii = forms.DateField(label='Data nasterii', required=False, 
                                    widget = forms.SelectDateWidget(years=range(1920, 2020)))
    email = forms.EmailField(label='Email', required=True)
    confirmare_email = forms.EmailField(label='Confirmare email', required=True)
    tip_mesaj = forms.ChoiceField(choices=[
        ('Reclamatie', 'Reclamatie'), 
        ('Intrebare', 'Intrebare'), 
        ('Review', 'Review'),
        ('Cerere', 'Cerere'),
        ('Programare', 'Programare'),
        ])
    subiect = forms.CharField(label='Subiect', max_length=50, required=True, validators=[validate_text])
    minim_zile_asteptare = forms.IntegerField(label='Minim zile asteptare', validators=[isPositive])
    mesaj = forms.CharField(widget=forms.Textarea, label='Mesaj (Introduceti semnatura, adica numele la sfarsit)', \
        initial='Va rog sa va semnati!')
    
    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        if (timezone.now().date() - data_nasterii).days / 365 < 18:
            raise forms.ValidationError("Expeditorul trebuie sa fie major")
        return data_nasterii
        
    def clean_mesaj(self):
        mesaj = self.cleaned_data.get('mesaj')
        nr_cuvinte = len(re.findall(r'\w+', mesaj))
        linkuri = r"https?://"
        are_link = re.findall(linkuri, mesaj)
        if are_link or nr_cuvinte < 5 or nr_cuvinte > 100:
            raise forms.ValidationError("Mesajul trebuie sa aiba intre 5 si 100 de cuvinte, fara linkuri")
        return mesaj
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirmare_email")
        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError("Adresele de email nu coincid.")
        
        mesaj = cleaned_data.get('mesaj')
        nume = cleaned_data.get('nume')
        if re.findall(r'\w+', mesaj)[-1] != nume:
            raise forms.ValidationError("Lipseste semnatura") 
        
        return cleaned_data
    
from .models import Film
from django.utils import timezone

class FilmForm(forms.ModelForm):
    link_IMDB = forms.URLField(required=True, validators=[hasLink])
    URL_imagine = forms.URLField(required=True, validators=[hasLink], help_text="URL pentru imaginea filmului")
    
    class Meta:
        model = Film
        fields = ['titlu', 'data_adaugare', 'data_aparitie', 'link_IMDB', 'URL_imagine']
        labels = {
            'titlu': 'Titlul filmului',
            'data_aparitie': 'Data aparitiei',
            'data_adaugare': 'Data adaugarii',
            'link_IMDB': 'Link IMDB',
            'URL_imagine': 'URL imagine',
        }
        error_messages = {
            'titlu': {
                'max_length': 'Titlul este prea lung!',
                'unique': 'Filmul exista deja.'
            },
        }
        
    def clean_data_adaugare(self):
        data_adaugare = self.cleaned_data.get('data_adaugare')
        if data_adaugare > timezone.now():
            raise forms.ValidationError("Data adaugarii nu poate fi in viitor")
        return data_adaugare
    
    def clean_title(self):  
        title = self.cleaned_data.get('titlu')
        if title[0].isalpha() and title[0].islower():
            raise forms.ValidationError("Titlul trebuie sa inceapa cu litera mare")
        return title

    def clean(self):
        cleaned_data = super().clean()
        data_aparitie = cleaned_data.get('data_aparitie')
        data_adaugare = cleaned_data.get('data_adaugare')
        print(data_adaugare)
        if data_aparitie > data_adaugare.date():
            raise forms.ValidationError("Data aparitiei invalida")
        return cleaned_data
    
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "password1", "telefon", 
                  "data_nastere", "student", "pensionar", "localitate", "password2"]

        labels = {
            'username': 'Nume de utilizator',
            'first_name': 'Prenume',
            'last_name': 'Nume',
            'email': 'Email',
            'password1': 'Parola',
            'telefon': 'Telefon',
            'data_nastere': 'Data nasterii',
            'student': 'Student',
            'pensionar': 'Pensionar',
            'localitate': 'Localitate',
            'password2': 'Confirmare parola',
        }
        
    first_name = forms.CharField(max_length=50, label='Prenume', validators=[validate_text])
    last_name = forms.CharField(max_length=50, label='Nume', validators=[validate_text])
    
    def clean_data_nastere(self):
        data_nastere = self.cleaned_data.get('data_nastere')
        if (timezone.now().date() - data_nastere).days / 365 < 18:
            raise forms.ValidationError("Utilizatorul trebuie sa fie major")
        return data_nastere
    
    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if len(telefon) != 10:
            raise forms.ValidationError("Numarul de telefon trebuie sa aiba 10 cifre")
        return telefon

    def clean(self):
        cleaned_data = super().clean()
        data_nastere = cleaned_data.get('data_nastere')
        pensionar = cleaned_data.get('pensionar')
        if ((timezone.now().date() - data_nastere).days / 365 < 65) and pensionar:
            raise forms.ValidationError("Prea tanar pentru pensionar")
        
        password = cleaned_data.get('password1')
        password_confirm = cleaned_data.get('password2')
        if password != password_confirm:
            raise forms.ValidationError("Parolele nu coincid")
        
        return cleaned_data
            
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    ramane_logat = forms.BooleanField(
        required=False,
        initial=False,
        label='Ramaneti logat'
    )

    def clean(self):        
        cleaned_data = super().clean()
        ramane_logat = self.cleaned_data.get('ramane_logat')
        return cleaned_data
    
from .models import Promotie, Categorie
    
class PromotieForm(forms.ModelForm):
    categorii = forms.ModelMultipleChoiceField(
        queryset=Categorie.objects.all(), 
        widget=forms.CheckboxSelectMultiple,
        initial=Categorie.objects.all()
    )
    
    class Meta:
        model = Promotie
        fields = ['nume', 'data_creare', 'data_expirare', 'discount', 'limita_utilizari', 'categorii']
        labels = {
            'nume': 'Nume promotie  ',
            'data_creare': 'Data crearii',
            'data_expirare': 'Data expirarii',
            'discount': 'Discount',
            'limita_utilizari': 'Limita utilizari',
            'categorii': 'Categorii',
        }
        error_messages = {
            'nume' : {
                'max_length': 'Numele trebuie sa aiba maxim 50 de caractere',
                'unique': 'Promotia cu acest nume exista deja',
            },
            'data_creare': {'required': 'Data crearii este obligatorie!'},
            'data_expirare': {'required': 'Data expirarii este obligatorie!'},
            'discount': {'required': 'Discountul este obligatoriu!'},
            'limita_utilizari': {'required': 'Limita utilizari este obligatorie!'},
        }
        
    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        checkIntegerInRange(discount, 0, 90)
        return discount
    
    def clean(self):
        cleaned_data = super().clean()
        data_creare = cleaned_data.get('data_creare')
        data_expirare = cleaned_data.get('data_expirare')
        if data_expirare < data_creare:
            raise forms.ValidationError("Data expirarii trebuie sa fie mai mare decat data crearii")
        return cleaned_data

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'is_staff', 'is_active', 'groups', 'user_permissions']

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        if self.current_user and not self.current_user.has_perm('auth.change_user_email'):
            self.fields['email'].widget.attrs['readonly'] = True