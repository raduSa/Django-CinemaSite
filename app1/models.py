from django.db import models
from django.utils import timezone
import uuid
from django.urls import reverse
    
'''class Ambalaj(models.Model):
    nume = models.CharField(max_length=20, unique=True)
    TiPURI_MATEIAL = [
        (1, 'plastic'),
        (2, 'hartie'),
        (3, 'carton'),
    ]
    material = models.CharField(max_length=20, choices=TiPURI_MATEIAL)
    pret = models.DecimalField(max_digits=3, decimal_places=2)'''
    
'''class Prajitura(models.Model):
    nume = models.CharField(max_length=50)
    descriere = models.TextField()
    pret = models.DecimalField(max_digits=8, decimal_places=2)
    gramaj = models.PositiveIntegerField(null=False)
    temperatura = models.IntegerField()
    TIPURI_PRODUS = [
        (1, 'cofetaire'),
        (2, 'brutarie'),
    ]
    tip_produs = models.CharField(max_length=50, choices=TIPURI_PRODUS, default=1)
    calorii = models.PositiveIntegerField(null=False, default=0)
    CATEGORII_PRAJITURA = [
        (1, 'comuna'),
        (2, 'rara'),
        (3, 'legendara'),
    ]
    categorie = models.CharField(max_length=10, choices=CATEGORII_PRAJITURA, default=1)
    pt_diabetici = models.BooleanField(default=False, null=False)
    imagine = models.CharField(max_length=300, null=True)
    data_adaugare = models.DateTimeField(default=timezone.now)
    ambalaj = models.ForeignKey(Ambalaj, on_delete=models.CASCADE, null=True)'''

'''class Ingrediente(models.Model):
    nume = models.CharField(max_length=30, unique=True)
    calorii = models.PositiveIntegerField()
    unitate = models.CharField(max_length=10)
    prajituri = models.ManyToManyField(Prajitura)'''
    
from datetime import timedelta
    
class Cinematograf(models.Model):
    oras = models.CharField(max_length=50)
    strada = models.CharField(max_length=50)
    numar = models.PositiveIntegerField()
    
    def __str__(self):
        return self.oras
    
TIPURI_SALA = [
    (60, 'Mica'),
    (90, 'Mare'),
]

class Sala(models.Model):
    numar = models.PositiveIntegerField()
    nr_locuri = models.PositiveIntegerField(choices=TIPURI_SALA, default=60)
    cinematograf = models.ForeignKey(Cinematograf, on_delete=models.CASCADE)
    
class Categorie(models.Model):
    nume = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nume
    
class Film(models.Model):
    titlu = models.CharField(max_length=50, unique=True)
    descriere = models.TextField(max_length=500, null=True)
    imagine = models.ImageField(upload_to='', null=True, default=None, blank=True)
    durata = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0), null=True)
    data_adaugare = models.DateTimeField(default=timezone.now, help_text="Format: YYYY-MM-DD HH:MM:SS")
    data_aparitie = models.DateField()
    secol_aparitie = models.PositiveIntegerField(blank=True, null=True)
    categorii = models.ManyToManyField(Categorie)
    
    def __str__(self):
        return self.titlu
    
    def get_absolute_url(self):
        return reverse('film', kwargs={'id': self.id})
    
class Actor(models.Model):
    nume = models.CharField(max_length=50, unique=True)
    descriere = models.TextField(null=True)
    filme = models.ManyToManyField(Film, related_name='actori')
    
    def __str__(self):
        return self.nume
    
    def get_absolute_url(self):
        return reverse('actor', kwargs={'id': self.id})  
    
class Difuzare(models.Model):
    timp_start = models.TimeField()
    este_3D = models.BooleanField(default=False)
    data = models.DateField(default=timezone.now, null=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    nr_locuri = models.PositiveIntegerField(default=0)
    pret_bilet = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        # set the number of available seats    
        self.nr_locuri = self.sala.nr_locuri
        # set price (20 if 3D, 15 otherwise)
        self.pret_bilet = 20 if self.este_3D else 15
        super().save(*args, **kwargs)
    
class Bilet(models.Model):
    pret = models.DecimalField(max_digits=4, decimal_places=2)
    nr_loc = models.PositiveIntegerField()
    data_cumparat = models.DateTimeField(default=timezone.now)
    difuzare = models.ForeignKey(Difuzare, on_delete=models.SET_NULL, null=True)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True)

class Discount(models.Model):
    valoare = models.PositiveIntegerField(default=0)
    tip = models.CharField(max_length=20, default='MISSING')
    
    def __str__(self):
        return self.tip
    
    
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class CustomUser(AbstractUser):
    telefon = models.CharField(max_length=10)
    data_nastere = models.DateField(null=True, blank=True)
    student = models.BooleanField(default=False)
    pensionar = models.BooleanField(default=False)
    localitate = models.CharField(max_length=50, null=True, blank=True)
    cod = models.CharField(max_length=100, null=True)
    email_confirmat = models.BooleanField(default=False, null=False)
    blocat = models.BooleanField(default=False, null=False)
    
    class Meta:
        permissions = (
            ('vizualizeaza_oferta', 'Vizualizeaza oferta'),
            ('block_user', 'Blocheaza utilizator'),
        )

class Vizualizari(models.Model):
    id_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    film = models.ForeignKey(Film, on_delete=models.SET_NULL, null=True)
    data_vizualizare = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        max_elements = 5
        if Vizualizari.objects.filter(id_user=self.id_user).count() >= max_elements:
            oldest_element = Vizualizari.objects.filter(id_user=self.id_user).order_by('data_vizualizare').first()
            oldest_element.delete()
        super().save(*args, **kwargs) 
        
    def __str__(self):
        str = self.id_user.username if self.id_user else 'DELETED'
        str += ' - '
        str += self.film.titlu if self.film else 'DELETED'
        return str
        
class Promotie(models.Model):
    nume = models.CharField(max_length=50, unique=True)
    data_creare = models.DateField(default=timezone.now)
    data_expirare = models.DateField(blank=False, null=False)
    discount = models.IntegerField(blank=False,default=0)
    limita_utilizari = models.PositiveIntegerField(blank=False, default=0)
    categorii = models.ManyToManyField('Categorie', related_name='promotii')
    
    def __str__(self):
        return self.nume
    
class Comanda(models.Model):
    id_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    nr_bilete = models.PositiveIntegerField()
    data = models.DateField(default=timezone.now)
    film = models.ForeignKey(Film, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        str = self.id_user.username if self.id_user else 'DELETED'
        str += ' - '
        str += self.film.titlu if self.film else 'DELETED'
        str += ' - '
        str += f"{self.nr_bilete}"
        return str