from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
import collections 
import logging

logger = logging.getLogger('app1')

def index(request):
	return HttpResponse("Hello")

from .models import Film
                
def filme(request):
    try:
        return render(request, "filme.html",
                    {
                        "filme":Film.objects.all(),
                    }
                    )
    except Exception as e:
        logger.critical(f"Could not show films: {e}")
        return HttpResponse("Eroare la afisarea filmelor")
    
# show filtered films
    
from .models import Vizualizari, Difuzare, Sala

from .forms import BileteForm

def bilete(request):
    if request.method == 'POST':
        form = BileteForm(request.POST)
        if form.is_valid():  
            nume = form.cleaned_data['nume']
            # check if a specific film is requested
            if nume:
                user_id = request.session['user_id'] if 'user_id' in request.session else None    
                logger.info(f"Showing {nume}... Accessed by user: {user_id}")
                # save view if user is logged in
                if user_id is not None:
                    try:
                        Vizualizari.objects.create(
                            film=Film.objects.get(titlu=nume), 
                            id_user=CustomUser.objects.get(id=user_id)
                        )
                    except Exception as e:
                        logger.error(f"Error saving view: {e}")
                    
            ora_inceput = form.cleaned_data['ora_inceput']
            este_3D = form.cleaned_data['este_3D']
            cinema = form.cleaned_data['cinema']
            
            try:
                messages.info(request, f"Filtre aplicate - cinema: {cinema}, titlu: {nume if nume else 'Toate'}, \
                              ora_inceput: {ora_inceput}, este_3D: {este_3D}...")
                # filter after film title
                if nume:
                    bilete = Difuzare.objects.filter(film__titlu=nume)
                else:
                    bilete = Difuzare.objects.all()
                # filter after time
                bilete = bilete.filter(timp_start__gte=ora_inceput)
                # filter after 3D
                if este_3D == 'both':
                    pass
                else:
                    bilete = bilete.filter(este_3D=este_3D)
                # filter after cinema
                bilete = bilete.filter(sala__cinematograf__oras=cinema)
                    
                return render(request, "bilete.html",
                    {
                        "nume": nume,
                        "bilete": bilete,
                    }
                    )      
            except Exception as e:
                logger.critical(f"Could not show {nume}: {e}")
    else:
        form = BileteForm()
    return render(request, 'alegeDifuzari.html', {'form': form,})
    
# save user messages
    
from .forms import ContactForm
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime
from time import time
import os
import json

def get_age(date_of_birth):
    today = datetime.now().date()
    diff = relativedelta(today, date_of_birth)
    return f"{diff.years} de ani si {diff.months} luni"
    
def process_message(message):
    message = re.sub(r'\s+', ' ', message.replace('\n', ' ')).strip()
    return message

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():  
            try:                
                # preprocess data
                data = form.cleaned_data
                data['varsta'] = get_age(data['data_nasterii'])
                data['mesaj'] = process_message(data['mesaj'])
                data.pop('confirmare_email')
                data.pop('data_nasterii')
                # create new json file
                timestamp = int(time())
                filename = f"mesaj_{timestamp}.json"
                filepath = os.path.join('mesaje', filename)
                with open(filepath, 'w') as file:
                    json.dump(data, file, indent=4)
                messages.success(request, 'Mesajul a fost trimis cu succes!')
            except Exception as e:
                mail_admins(
                    subject='Eroare in salvarea mesajului',
                    message = f"A apărut o eroare: {e}",
                    html_message = f"<h1 style='color:red;'>Eroare in salvarea mesajului</h1><p>Error: {e}</p>",
                    fail_silently=False
                )
                logger.error(f"Error saving message: {e}")
                messages.error(request, 'Eroare in salvarea mesajului')
            return render(request, 'contact.html', {'form': ContactForm()})
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def mesaj_primit(request):
    return HttpResponse('Mesaj Primit!')

# add films

from .forms import FilmForm
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

def process_IMDB_link(link):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
    
    descriere = duratia = None
    
    response = requests.get(link, headers=headers)
    
    if response.status_code != 200:
        logger.warning(f"IMDB_link not found: {link}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    target_div = soup.find('div', class_='sc-70a366cc-0 bxYZmb')
    try:
        li_tags = target_div.find_all('li')
        if len(li_tags) >= 3:
            duratia = li_tags[2].text
    except AttributeError:
        logger.warning(f"Duration not found: {link}")
        return "Duratia nu a fost gasita"
    
    try:
        span = soup.find('span', class_='sc-3ac15c8d-0 hRUoSB')
        descriere = span.text
    except AttributeError:
        logger.warning(f"Description not found: {link}")
        return "Descrierea nu a fost gasita"
    
    # get the duration as timedelta obj
    hours, minutes, seconds = 0, 0, 0
    for num in duratia.split():
        if num[-1] == 'h':
            hours = int(num[:-1])
        elif num[-1] == 'm':
            minutes = int(num[:-1])
        elif num[-1] == 's':
            seconds = int(num[:-1])      
    duratia = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    
    # trim description
    if len(descriere) > 500:
        descriere = descriere[:496] + '...'
        
    return duratia, descriere

def introdu_film(request):
    # check if user has permission to add a film
    if not request.user.has_perm('app1.add_film'):
        if request.user:
            logger.warning(f"Unauthorized user {request.user.username} tried to add a film")
        return error_403(request, message="Nu ai voie sa adaugi filme", title="Eroare adaugare produse")
    
    if request.method == 'POST':
        form = FilmForm(request.POST)
        if form.is_valid():
            film = form.save(commit=False)
            try:
                link_IMDB = form.cleaned_data.get('link_IMDB')
                image_URL = form.cleaned_data.get('URL_imagine')
                
                try:
                    response = requests.get(image_URL)
                    response.raise_for_status()
                    
                    image_content = ContentFile(response.content)
                    film.imagine.save(f"{film.titlu}.png", image_content)
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Error downloading the image: {image_URL}")
                    form.add_error('image_url', f"Error downloading the image: {e}")
                    
                film.durata, film.descriere = process_IMDB_link(link_IMDB)
                film.secol_aparitie = film.data_aparitie.year // 100 + 1
                film.save()
                messages.debug(request, f"Film {film.titlu} has been added")    
            except Exception as e:
                logger.error(f"Error saving film {film.titlu}: {e}")
                messages.error(request, f"Error saving film {film.titlu}: {e}")
            return render(request, 'introduFilm.html', {'form': FilmForm()})
    else:
        form = FilmForm()
    return render(request, 'introduFilm.html', {'form': form})

# account management (creation, login, logout, change password, profile)

def home(request):
    return render(request, 'home.html')

import random
import string

def get_random_string(max_length):
    length = random.randint(50, max_length)
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_string

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

def send_confirmation_email(request, email, cod, username, nume, prenume):
    try:
        domain = request.get_host()
        
        url_imagine = f"http://{domain}{settings.STATIC_URL}images/logo_test.png"
        print(url_imagine)
        context = {'nume': nume, 'prenume': prenume, 'username': username, 'cod': cod, 
                'confirmation_link': 'http://localhost:8000/app1/confirm_email/' + cod,
                'url_imagine': url_imagine}  
        html_content = render_to_string('email_template.html', context)

        email = EmailMessage(
            subject='Confirmare Email',
            body=html_content,
            from_email='test.webapp.ceva@gmail.com',
            to=[email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
    except Exception as e:
        logger.critical(f"Error sending confirmation email: {e}")

from .forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # cannot allow username 'admin'
                if user.username == 'admin':
                    email = user.email
                    mail_admins(
                        subject='Cineva incearca sa ne preia site-ul',
                        message = f"Email: {email}",
                        html_message = f"<h1 style='color:red;'>Cineva incearca sa ne preia site-ul</h1><p>Email: {email}</p>",
                        fail_silently=False
                    )
                    return HttpResponse("Nu poti crea un user cu username 'admin'")
                
                user.cod = get_random_string(100)
                user.save()
            except Exception as e:
                logger.critical(f"Error saving user: {e}")
                messages.warning(request, f"Userul nu a putut fi salvat")
            send_confirmation_email(request, user.email, user.cod, user.username, user.first_name, user.last_name)
            messages.success(request, f"Userul {user.username} a fost inregistrat cu succes")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                print(f"Field: {field}, Errors: {', '.join(errors)}")
            if form.non_field_errors():
                print(f"Non-field errors: {form.non_field_errors()}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


from django.contrib.auth import login, logout
from .forms import CustomAuthenticationForm
from django.core.mail import mail_admins
from django.utils.timezone import now

login_attempts = collections.defaultdict(list)

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            # check if email is confirmed
            if not user.email_confirmat:
                return HttpResponse("Emailul nu a fost confirmat!")
            # check if user has been blocked
            if user.blocat:
                return error_403(request, message="Contul acesta a fost blocat", title="Cont Blocat")
            login(request, user)
            # store user information in session
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['nume'] = user.first_name
            request.session['prenume'] = user.last_name
            request.session['telefon'] = user.telefon
            request.session['localitate'] = user.localitate
            logger.info(f"User {user.username} logged in")
            if not form.cleaned_data.get('ramane_logat'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(24*60*60)          
            return redirect('profile')
        else:
            username = form.cleaned_data.get('username')
            # get ip address
            ip = None
            try:
                req_headers = request.META
                x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for_value:
                    ip = x_forwarded_for_value.split(',')[-1].strip()
                else:
                    ip = req_headers.get('REMOTE_ADDR')
            except Exception as e:
                logger.error(f"Error getting ip address for user {username}: {e}")
            login_attempts[username].append((ip, now()))
            # remove attempts older than 2 minutes
            login_attempts[username] = [
                attempt for attempt in login_attempts[username]
                if (now() - attempt[1]).total_seconds() < 120
            ]
            logger.debug(f"Login attempts for user {username}: {login_attempts[username]}")
            # warn user if they have made too many failed attempts
            if len(login_attempts[username]) < 3:
                messages.info(request, f"Logare esuata - {username}. Incercari ramase - \
                        {3 - len(login_attempts[username])}")
            else:
                messages.warning(request, f"Logare esuata - {username}. Admini avertizati!")
            # if user has made 3 failed attempts in the last 2 minutes
            if len(login_attempts[username]) >= 3:
                mail_admins(
                    subject='Logari suspecte',
                    message = f"Username: {username}\nIP: {ip}",
                    html_message = f"<h1 style='color:red;'>Logari suspecte</h1><p>Username: {username}</p><p>IP: {ip}</p>",
                    fail_silently=False
                )
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    permission = Permission.objects.get(codename='vizualizeaza_oferta')
    request.user.user_permissions.remove(permission)
    logout(request)
    logger.info(f"User {request.user.username} logged out")
    request.session.clear()
    return redirect('home')

def profile_view(request):
    username = request.session.get('username')
    nume = request.session.get('nume')
    prenume = request.session.get('prenume')
    telefon = request.session.get('telefon')
    localitate = request.session.get('localitate')
    email = request.session.get('email')
    
    # check if user is logged in
    if not username:
        return redirect('login')

    return render(request, 'profile.html', {
        'username': username,
        'email': email,
        'nume': nume,
        'prenume': prenume,
        'telefon': telefon,
        'localitate': localitate
    })
    
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            logger.info(f"User {request.user.username} changed password")
            messages.success(request, 'Parola a fost actualizata')
            return redirect('home')
        else:
            messages.error(request, 'Exista erori.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

# confirm user email function

from .models import CustomUser

def confirm_email(request, cod):
    user = CustomUser.objects.filter(cod=cod).first()
    if user:
        user.email_confirmat = True
        user.save()
        logger.info(f"User {user.username} confirmed email")
        return HttpResponse("Email confirmat cu succes")
    else:
        return HttpResponse("Nu exista user cu acest cod")
    
from .forms import PromotieForm   
from .models import Categorie

# auto send mails for promos

promo_templates = {
'Actiune': '''Bună, {}! 
Avem o ofertă specială pentru tine! Nu rata ocazia de a viziona filme pline de adrenalina, cu discounturi de până la {}%.
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',
        
'Drama': '''Bună, {}! 
Descoperă povești emoționante și captivante, acum la prețuri speciale! Bucură-te de reduceri de până la {}% la cele mai bune filme dramatice. 
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

'Thriller': '''Bună, {}! 
Ține-ți respirația și intră în lumea suspansului! Filmele thriller preferate sunt acum disponibile cu reduceri de până la {}%. 
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

'Science Fiction': '''Bună, {}! 
Explorează lumi uimitoare și tehnologii fantastice! Bucură-te de cele mai bune filme science fiction, acum cu reduceri de până la {}%.
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

'Comedie': '''Bună, {}! 
Râzi cu poftă alături de noi! Cele mai bune comedii sunt acum disponibile cu reduceri de până la {}%. 
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

'Crimă': '''Bună, {}! 
Intră în lumea intrigilor și investigațiilor fascinante! Filmele din categoria Crimă te așteaptă cu reduceri de până la {}%. 
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

'Horror': '''Bună, {}! 
Pregătește-te să simți fiori reci! Cele mai înspăimântătoare filme horror sunt acum disponibile cu reduceri de până la {}%. 
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

'Biografie': '''Bună, {}! 
Descoperă povești de viață inspiraționale! Bucură-te de filmele biografice preferate, acum cu reduceri de până la {}%. 
Oferta este valabilă până pe {} pentru urmatoarele categorii de filme: {}.
Grăbește-te! Doar primii {} clienti pot beneficia de această promoție exclusivă!''',

}

def add_mail_to_list(mail_list, nume, limita_utilizari, username, discount, data_expirare, email, most_viewed_category, promo_categories):
    subject = f'Email Promoțional - {nume}'
    message = promo_templates[most_viewed_category]. \
        format(username, discount, data_expirare, ', '.join(promo_categories), limita_utilizari)
    from_email = 'test.webapp.ceva@gmail.com'
    recipient_list = [email]
    mail_list.append((subject, message, from_email, recipient_list))    
    return mail_list

from django.core.mail import send_mass_mail

def promotii(request):
    if request.method == 'POST':
        form = PromotieForm(request.POST)
        if form.is_valid():
            try:
                promotie = form.save(commit=False)
                mail_list = list()
                # get promotion categories
                promo_categories = form.cleaned_data['categorii']
                promo_categories = [category.nume for category in promo_categories]
                logger.debug(f"Creating new promotion: {promotie.nume} - Promo categories: {promo_categories}")
                
                # get each user's most viewed category
                for user in CustomUser.objects.all():
                    views = Vizualizari.objects.filter(id_user=user.id)
                    if views.exists():
                        views_per_category = collections.defaultdict(int)
                        for view in views:
                            if view.film and view.film.categorii.exists():
                                for category in view.film.categorii.all():
                                    views_per_category[category.nume] += 1
                        logger.debug(f"User: {user.username} - Views per category: {views_per_category}")
                        # get most viewed category with count >= 3 and part of promo_categoires
                        # and add mail to mail_list
                        most_viewed_category = max(views_per_category, 
                            key=lambda key: views_per_category[key] if key in promo_categories else 0)

                        if views_per_category[most_viewed_category] >= 3:
                            add_mail_to_list(mail_list, promotie.nume, promotie.limita_utilizari, user.username, \
                                promotie.discount, promotie.data_expirare, user.email, most_viewed_category, promo_categories)
                # send mails
                send_mass_mail(mail_list, fail_silently=False)
                promotie.save()
                # save many to many
                form.save_m2m()
                messages.debug(request, f"Promotie {promotie.nume} creata")
            except Exception as e:
                logger.error(f"Error creating promotion: {e}")
                messages.error(request, f"Promotia {promotie.nume} nu a putut fi creata")
            return render(request, 'promotii.html', {'form': PromotieForm()})
    else:
        form = PromotieForm()
    return render(request, 'promotii.html', {'form': form})

def afisare_pagina(request):
    if not request.user.has_perm('app1.view_film'):
        return HttpResponseForbidden("Nu ai voie aici! Pa!")
    return redirect('filme')

def error_403(request, message=None, title=None):
    return HttpResponseForbidden(render(request, '403.html', context={
        'message': message,
        'title': title
    }))
    
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission

@permission_required('app1.vizualizeaza_oferta', raise_exception=True)
def oferta(request):
    logger.debug(f"Promo accessed by user: {request.user.username}")
    return render(request, 'oferta.html')

def permisiune_oferta(request):
    permission = Permission.objects.get(codename='vizualizeaza_oferta')
    request.user.user_permissions.add(permission)
    return redirect('oferta')

# test messages framework
def test_messages(request):
    messages.info(request, 'Test message')
    return render(request, 'test_messages.html')

from .models import Actor

# show details for a specific film and actor
def actor(request, id):
    actor = Actor.objects.get(id=id)
    film_list = actor.filme.all()
    return render(request, 'actor_details.html', {'actor': actor, 'film_list': film_list})

def film(request, id):
    film = Film.objects.get(id=id)
    category_list = film.categorii.all()
    actor_list = film.actori.all()
    return render(request, 'film_details.html', {
        'film': film, 
        'category_list': category_list,
        'actor_list': actor_list,
    })

def promotie(request, id):
    promotie = Promotie.objects.get(id=id)
    category_list = promotie.categorii.all()
    return render(request, 'promotie_details.html', {
        'promotie': promotie,
        'category_list': category_list
    })

from django.http import JsonResponse
from .models import Promotie, Categorie
from django.utils import timezone
from django.db.models import F

# return relevant data for 'difuzare' objects for shopping cart view
def get_difuzare_data(request):
    if request.method == "GET":
        try:
            tickets = Difuzare.objects.all().values("id", "timp_start", "film__titlu", "sala__numar", "pret_bilet")

            # get promotions that can still be applied
            promos = Promotie.objects.filter(
                    limita_utilizari__gt=0,
                    data_expirare__gte=timezone.now()
                ).values("id", "discount", "limita_utilizari", "categorii")
            
            # get the biggest discount for each category of film from promotions
            discounts = dict() # category_id -> discount
            used_promos = dict() # category_id -> promotion_id
            for promo in promos:
                if promo['categorii'] and promo['discount'] > discounts.get(promo['categorii'], 0):
                    discounts[promo['categorii']] = promo['discount']
                    used_promos[promo['categorii']] = promo['id']
            logger.debug(f"Category based discounts: {discounts}")
            
            # update prices based on discounts
            for ticket in tickets:
                film = Film.objects.get(titlu=ticket['film__titlu'])
                # get biggest discount for the film based on its categories
                film_categories = [entry['id'] for entry in list(film.categorii.all().values("id"))]
                category_discounts = [discounts.get(category, 0) \
                    for category in film_categories]                
                max_discount = max(category_discounts, default=0) / 100
                # add discount if buyer is student or pensioner
                if request.user.student:
                    max_discount += 0.2
                if request.user.pensionar:
                    max_discount += 0.15
                    
                ticket['pret_bilet'] = float(ticket['pret_bilet']) * max(1 - max_discount, 0)
            
            # subtract from number of uses for each used promotion object
            to_subtract = {used_promos[category_id] for category_id in used_promos}
            Promotie.objects.filter(id__in=to_subtract).update(limita_utilizari=F('limita_utilizari') - 1)
            
            # get data about used promotions
            used_promos_data = list()
            for category_id in used_promos:
                promo = Promotie.objects.get(id=used_promos[category_id])
                category = Categorie.objects.get(id=category_id)
                used_promos_data.append({
                    'category': category.nume,
                    'discount': promo.discount,
                    'name': promo.nume,
                    'id': promo.id
                })
            logger.debug(f"Used promotions data: {used_promos_data}")
                
            json_data = {'tickets': list(tickets), 'promos': used_promos_data}
                        
            return JsonResponse(json_data, safe=False)
        except Exception as e:
            logger.error(f"Error getting difuzare data: {e}")
    
# show shopping cart
def shopping_cart(request):
    # user must be logged in to buy tickets
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'shopping_cart.html')


# save users order in database and send pdf with details
from reportlab.pdfgen import canvas    
from reportlab.lib.pagesizes import letter
from .models import Cinematograf
from Proiect.settings import ADMINS

def fisier_pdf(request, ticket_data, pdf_path):
    p = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    try:
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "Factura de Cumparere")
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 70, f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # User details
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 100, "Detalii utilizator:")
        p.drawString(70, height - 120, f"Nume: {request.user.first_name}")
        p.drawString(70, height - 140, f"Prenume: {request.user.last_name}")
        p.drawString(70, height - 160, f"Email: {request.user.last_name}")
        
        # Admin email
        p.drawString(50, height - 200, f"Email administrator: {ADMINS[1][1]}")
        
        # Order details
        y_position = height - 240
        total_items = 0
        total_price = 0.0

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Bilete cumparate:")
        y_position -= 20
        
        p.setFont("Helvetica", 10)
        for ticket in ticket_data:
            # Create a new page if needed
            if y_position < 100:  
                p.showPage()
                y_position = height - 50

            # get necessary data from database and json
            film = Film.objects.get(titlu=ticket['film__titlu'])
            difuzare = Difuzare.objects.get(id=ticket['id'])
            cinema = Cinematograf.objects.get(id=difuzare.sala.cinematograf.id)
            cinema_city = cinema.oras
            cinema_street = cinema.strada
            cinema_street_nr = cinema.numar
            film_link = 'http://localhost:8000/app1/film/' + str(film.id)
            film_name = ticket['film__titlu']
            number_of_tickets = ticket['nr_bilete']
            ticket_price = ticket['pret_bilet']
            subtotal = number_of_tickets * float(ticket_price)

            # Add product details
            p.drawString(50, y_position, f"Film: {film_name}")
            y_position -= 20
            p.drawString(50, y_position, f"Adresa cinematograf: {cinema_city}, {cinema_street} {cinema_street_nr}")
            y_position -= 20
            p.drawString(70, y_position, f"Link film: {film_link}")
            y_position -= 20
            p.drawString(70, y_position, f"Cantitate: {number_of_tickets}")
            y_position -= 20
            p.drawString(70, y_position, f"Pret Unitar: {ticket_price:.2f}")
            y_position -= 20
            p.drawString(70, y_position, f"Subtotal: {subtotal}")
            y_position -= 40

            total_items += number_of_tickets
            total_price += subtotal
            
        # Totals
        if y_position < 50:  
            p.showPage()
            y_position = height - 50
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, f"Total Produse: {total_items}")
        y_position -= 20
        p.drawString(50, y_position, f"Pret Final: {total_price}")
        y_position -= 40
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        
    p.showPage()
    p.save()
   
from django.core.mail import EmailMessage
def trimite_mail_pdf(request, ticket_data):
    email = EmailMessage(
        subject='Factura de cumparare',
        body='Buna ziua',
        to=[request.user.email],
    )
    
    # create path for pdf
    base_folder = os.path.join(settings.BASE_DIR, "temporar-facturi")
    user_folder = os.path.join(base_folder, request.user.username)
    # create user folder if it doesn't exist
    os.makedirs(user_folder, exist_ok=True)
    filename = f"factura-{int(time())}.pdf"
    pdf_path = os.path.join(user_folder, filename)
    
    fisier_pdf(request, ticket_data, pdf_path)
    
    email.attach_file(pdf_path)
    email.send()

from .models import Comanda
      
def proceseaza_date(request):
    if request.method=="POST":
        try:
            ticket_data = json.loads(request.body.decode("utf-8"))
            logger.debug(f"Ticket data: {ticket_data}")
            # save the order to database
            for ticket in ticket_data:
                Comanda.objects.create(
                    id_user=request.user,
                    nr_bilete=ticket['nr_bilete'],
                    film=Film.objects.get(titlu=ticket['film__titlu']),
                )
            # send pdf via email with details
            trimite_mail_pdf(request, ticket_data)
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return HttpResponse("Datele nu au fost procesate.")
    return HttpResponse("Totul in regula. Datele au fost procesate.")

def menu(request):
    return render(request, 'menu.html')