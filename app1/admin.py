from django.contrib import admin

from .models import Cinematograf, Sala, Film, Difuzare, Actor, Bilet, \
    Discount, CustomUser, Vizualizari, Categorie, Promotie, Comanda
    
from django.contrib.auth.admin import UserAdmin

admin.site.site_header = "Panou de Administrare Site"
admin.site.site_title = "Admin Site"
admin.site.index_title = "Panoul de administrare"

'''from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin'''

class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('student', 'pensionar', 'localitate', 'telefon', 'data_nastere', 
                       'email_confirmat', 'cod', 'blocat'),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        # can only block/unblock users if user has permission
        if not request.user.has_perm('app1.block_user'):
            readonly_fields = list(readonly_fields) + ['blocat']

        return readonly_fields

    
admin.site.register(CustomUser, CustomUserAdmin)

class CinematografAdmin(admin.ModelAdmin):
    search_fields = ('oras', 'strada', 'numar',)

admin.site.register(Cinematograf, CinematografAdmin)

class SalaAdmin(admin.ModelAdmin):
    search_fields = ('cinematograf__oras', 'numar',)
    
admin.site.register(Sala, SalaAdmin)

class FilmAdmin(admin.ModelAdmin):
    ordering = ('data_aparitie',)
    search_fields = ('titlu', 'categorii__nume', )
    list_filter = ('data_aparitie', 'secol_aparitie', 'titlu', 'durata',)
    fieldsets = (
        ('Informații Generale', {
            'fields': ('titlu', 'descriere', 'categorii',),
        }),
        ('Date Publicare', {
            'fields': ('data_aparitie', 'secol_aparitie', 'data_adaugare',),
            'classes': ('collapse',),
        }),
        ('Extra', {
            'fields': ('durata', 'imagine',)
        })
    )

    
admin.site.register(Film, FilmAdmin)

class DifuzareAdmin(admin.ModelAdmin):
    search_fields = ('film__titlu', 'sala__numar', 'timp_start',)
    list_filter = ('sala__cinematograf__oras', 'film__titlu', 'timp_start',)

admin.site.register(Difuzare, DifuzareAdmin)

class ActorAdmin(admin.ModelAdmin):
    search_fields = ('nume',)
    
admin.site.register(Actor, ActorAdmin)

class BiletAdmin(admin.ModelAdmin):
    search_fields = ('data_cumparat',)
    
admin.site.register(Bilet, BiletAdmin)

class DiscountAdmin(admin.ModelAdmin):
    search_fields = ('valoare',)
    
admin.site.register(Discount, DiscountAdmin)

class VizualizariAdmin(admin.ModelAdmin):
    search_fields = ('film__titlu', 'id_user',)
    
admin.site.register(Vizualizari, VizualizariAdmin)

class CategorieAdmin(admin.ModelAdmin):
    search_fields = ('nume',)
    
admin.site.register(Categorie, CategorieAdmin)

class PromotieAdmin(admin.ModelAdmin):
    search_fields = ('categorii__nume',)
    
admin.site.register(Promotie, PromotieAdmin)

class ComandaAdmin(admin.ModelAdmin):
    search_fields = ('user_id__username',)
    
admin.site.register(Comanda, ComandaAdmin)