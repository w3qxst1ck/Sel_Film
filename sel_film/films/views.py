from django.core.mail import send_mail, BadHeaderError
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from string import ascii_lowercase
from django.views.decorators.cache import cache_page
import logging

from serials.models import Serial
from .models import Film, Genre, Actor, Director, Country
from .forms import Film1FindForm, Film2FindForm
from .service import find_films


logger = logging.getLogger(__name__)


def index_page(request):
    logger.info('Запущена index page')
    return render(request, 'films/index.html')


class FilmListView(generic.ListView):
    model = Film
    context_object_name = 'films'
    paginate_by = 6

    def get_queryset(self):
        genres = Genre.objects.only('title')
        films = Film.objects.only('title_ru', 'title_en', 'year', 'image', 'plot')\
            .prefetch_related(Prefetch('genres', queryset=genres)).order_by('-rating')
        return films


class FilmDetailView(generic.DetailView):
    model = Film
    context_object_name = 'film'

    def get_object(self, queryset=None):
        genres = Genre.objects.only('title')
        actors = Actor.objects.only('first_name', 'last_name')
        directors = Director.objects.only('first_name', 'last_name')
        countries = Country.objects.only('title')
        film = Film.objects.filter(id=self.kwargs['pk']).prefetch_related(Prefetch('genres', queryset=genres))\
            .prefetch_related(Prefetch('actors', queryset=actors))\
            .prefetch_related(Prefetch('directors', queryset=directors))\
            .prefetch_related(Prefetch('countries', queryset=countries))[0]
        return film


def search_films(request):

    if request.method == 'POST':
        context = {}
        form_1 = Film1FindForm(request.POST)
        form_2 = Film2FindForm(request.POST)
        film_1 = None
        film_2 = None
        logger.info('Сделан запрос на подборку для фильмов')

        if form_1.is_valid():
            try:
                film_1 = Film.objects.only('title_ru', 'image', 'year').\
                    filter(title_ru__iexact=form_1.cleaned_data['film_1_title_ru'])[0]

                context['film_1'] = film_1
                logger.info(f'Искали фильм 1: {film_1}')

            except IndexError:
                context['films_1_query'] = Film.objects.only('title_ru', 'image', 'year')\
                    .filter(title_ru__icontains=form_1.cleaned_data['film_1_title_ru']).order_by('-rating')[:5]
                # log
                logger.info(f'Не удалось найти фильм 1: {form_1.cleaned_data["film_1_title_ru"]}, но подобран queryset {[film for film in context["films_1_query"]]}')
                if not context['films_1_query']:
                    logger.warning(f'Не найдет film и queryset по запросу фильма 1: {form_1.cleaned_data["film_1_title_ru"]}')

        if form_2.is_valid():
            try:
                film_2 = Film.objects.only('title_ru', 'image', 'year')\
                    .filter(title_ru__iexact=form_2.cleaned_data['film_2_title_ru'])[0]

                context['film_2'] = film_2
                logger.info(f'Искали фильм 2: {film_2}')

            except IndexError:
                context['films_2_query'] = Film.objects.only('title_ru', 'image', 'year')\
                    .filter(title_ru__icontains=form_2.cleaned_data['film_2_title_ru']).order_by('-rating')[:5]
                # log
                logger.info(f'Не удалось найти фильм 2: {form_2.cleaned_data["film_2_title_ru"]}, но подобран queryset {[film for film in context["films_2_query"]]}')
                if not context['films_2_query']:
                    logger.warning(f'Не найдет film и queryset по запросу фильма 2: {form_2.cleaned_data["film_2_title_ru"]}')

        if film_1 and film_2 and film_1 == film_2:
            logger.info('В подборку включены два одиннаковых фильма')
            context['films_duplicate'] = True

        elif film_1 and film_2:
            top_ten_points = find_films(id_1=film_1.id, id_2=film_2.id)
            context['top_ten'] = Film.objects.only('title_ru', 'year', 'image')\
                .filter(id__in=[id for id, _ in top_ten_points])

        context['form_1'] = form_1
        context['form_2'] = form_2

        return render(request, 'films/search_films.html', context)

    else:
        form_1 = Film1FindForm()
        form_2 = Film2FindForm()
        return render(request, 'films/search_films.html', context={
                                                                    'form_1': form_1,
                                                                    'form_2': form_2,
                                                                   })


def search(request):
    if request.method == "POST":
        context = {}
        search_data = request.POST['search_data']
        search_data_lower = request.POST['search_data'].lower()
        model_type = request.POST['currency']

        if model_type == 'Films':
            try:
                if search_data_lower[0] in ascii_lowercase:
                    films_list = Film.objects.filter(title_en__icontains=search_data_lower).order_by('-rating')[:20]
                else:
                    films_list = Film.objects.filter(title_ru__icontains=search_data_lower).order_by('-rating')[:20]
            except IndexError:
                films_list = []
        else:
            try:
                if search_data_lower[0] in ascii_lowercase:
                    films_list = Serial.objects.filter(title_en__icontains=search_data_lower).order_by('-rating')[:20]
                else:
                    films_list = Serial.objects.filter(title_ru__icontains=search_data_lower).order_by('-rating')[:20]
            except IndexError:
                films_list = []

        context['films'] = films_list
        context['search_data'] = search_data
        return render(request, 'search_results.html', context)
    else:
        return render(request, 'search_results.html')


def about_page(request):
    if request.method == 'POST':
        message_name = request.POST.get('name', '')
        message_email = request.POST.get('email', '')
        message_text = request.POST.get('message', '')
        if message_text and message_email and message_name:
            try:
                send_mail(
                    message_name,
                    message_text,
                    message_email,
                    ['w3qxnkst1ck@gmail.com', 'hizenberg2282@gmail.com']
                )
                return render(request, 'about.html', {'message_name': message_name})
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
    else:
        return render(request, 'about.html')