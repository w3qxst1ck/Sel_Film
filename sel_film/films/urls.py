from django.urls import path
from django.views.decorators.cache import cache_page

from django.conf import settings
from .views import index_page, FilmDetailView, search_films, search, contact_page, FilmListView, \
    FilterFilmListView, about_page

urlpatterns = [
    path('', index_page, name='index-page'),
    path('contacts/', contact_page, name='contact-page'),
    path('about/', about_page, name='about-page'),
    path('films/', FilmListView.as_view(), name='film-list'),
    path('films/<int:pk>/', FilmDetailView.as_view(), name='film-detail'),
    path('films/search_films/', search_films, name='search-films'),
    path('filter_search/', FilterFilmListView.as_view(), name='filter-search'),
]


