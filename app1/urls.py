from django.urls import path, re_path
from . import views

urlpatterns = [
	path("", views.index, name="index"),
	path("filme", views.filme, name="filme"),
 	path("bilete", views.bilete, name="bilete"),
	#lab5
	path("contact", views.contact, name="contact"),
	path("mesaj_primit", views.mesaj_primit, name="mesaj trimis"),
	path("introdu_film", views.introdu_film, name="introdu film"),
	#lab6
	path("login", views.custom_login_view, name="login"),
	path("logout", views.logout_view, name="logout"),
    path("home", views.home, name="home"),
    path("register", views.register_view, name="register"),
    path("profile", views.profile_view, name="profile"),
    path("change_password", views.change_password_view, name="change_password"),
    #lab7
    path("confirm_email/<str:cod>", views.confirm_email, name="confirm_email"),
    path("promotii", views.promotii, name="promotii"),
    #lab8
    path("afis_filme", views.afisare_pagina, name="afis_filme"),
    path("403", views.error_403, name="error_403"),
    path("permisiune_oferta", views.permisiune_oferta, name="permisiune_oferta"),
    path("oferta", views.oferta, name="oferta"),
    #lab_9
    path('test_messages', views.test_messages, name='test_messages'),
    path('actor/<int:id>', views.actor, name='actor'),
    path('film/<int:id>', views.film, name='film'),
    path('promotie/<int:id>', views.promotie, name='promotie'),
    #lab_10
    path('get_difuzare_data', views.get_difuzare_data, name='get_difuzare_data'),
    path('shopping_cart', views.shopping_cart, name='shopping_cart'),
    #lab_11
    path("proceseaza_date", views.proceseaza_date, name="proceseaza_date"),
    #lab_12
    path("menu", views.menu, name="menu"),
]
