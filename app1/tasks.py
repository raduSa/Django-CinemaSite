import schedule
import time
import django
import os
import logging

logger = logging.getLogger('app1')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proiect.settings')
django.setup()

from django.utils import timezone
from .models import CustomUser

# delete users who have not confirmed email
def delete_users():
    CustomUser.objects.filter(email_confirmat=False).delete()
    logger.info(f"Deleted users who have not confirmed email")
    print('now')
    
from django.core.mail import send_mail
from .models import Film

# send newsletter
def send_newsletter():
    emails = CustomUser.objects. \
        filter(date_joined__lt=timezone.now() - timezone.timedelta(days=7)).values_list('email', flat=True)
    subject = f'Newsletter'
    film_titles = Film.objects.all().values_list('titlu', flat=True)
    message = 'Verifica pagina web pentru filmele urmatoare: ' + ', '.join(film_titles)
    from_email = 'test.webapp.ceva@gmail.com'
    recipient_list = [*set(emails)]
    logger.debug(f"Newsletter Recipients: {recipient_list}")
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    logger.info(f"Sending newsletter to {set(emails)}")
    print('sent')
    
from .models import Difuzare, Sala
import random
import datetime as datetime
    
# create random film schedule for each cinema
def create_film_schedule():
    # delete previous schedule
    Difuzare.objects.all().delete()
    logger.debug(f"Deleted previous film schedule")
    
    for sala in Sala.objects.all():
        films = list(Film.objects.all().values_list('id', 'durata'))
        current_time = datetime.time(8, 0)
        current_time = datetime.datetime.combine(datetime.datetime.today(), current_time)
        
        while current_time.time() < datetime.time(14, 0):
            # add break between films
            break_time = random.randint(1, 30)
            current_time = current_time + datetime.timedelta(minutes=break_time)
            if current_time.time() >= datetime.time(14, 0):
                break
            # choose random film and add to schedule
            film = random.choice(films)
            films.remove(film)
            is_3D = random.choice([True, False])
            Difuzare.objects.create(film_id=film[0], sala_id=sala.id, timp_start=current_time.time(), este_3D=is_3D)
            current_time = current_time + film[1]
            
    logger.info(f"Created random film schedule for each cinema")
    
from Proiect.settings import BASE_DIR
from django.core.mail import mail_admins
import re
from time import time
    
# remind admins about recieved messages
def remind_admins():
    path = os.path.join(BASE_DIR, 'mesaje')
    # get messages sent in last 30 minutes
    messages = [f for f in os.listdir(path) if (int(time()) - 30 * 60) < int(re.search(r'\d+', f).group())]
    logger.debug(f"Found new messages: {messages} - time: {time()}")
    if len(messages) > 0:
        mail_admins(
            subject='Mesaje noi',
            message = f"{len(messages)} mesaje noi. Verifica mesajele!\n",
            fail_silently=False
        )
    logger.info(f"Reminding admins about recieved messages")
    