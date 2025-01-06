from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app1.models import Actor, Film

class ActorSitemap(Sitemap):
    changefreq = "yearly"  
    
    priority = 0.8        

    def items(self):
        return Actor.objects.all()
    
class FilmSitemap(Sitemap):
    changefreq = "yearly"  
    
    priority = 0.8        

    def items(self):
        return Film.objects.all()
    
    def lastmod(self, obj):
        return obj.data_adaugare

class VederiStaticeSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1

    def items(self):
        return ['contact', 'filme']

    def location(self, item):
        return reverse(item)