# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import ListView
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from .models import Movie
from .forms import MoviePageForm


class MovieListView(ListView):
    queryset = Movie.active.all().order_by('title')
    context_object_name = 'movies'
    paginate_by = 4
    template_name = 'movie/list.html'

    def get_context_data(self, **kwargs):
        context = super(MovieListView, self).get_context_data(**kwargs)
        last_visit = self.request.session.get('latest_visit')

        if last_visit:
            # If user already visited,
            # then visit_to_print = latest_visit
            # and update latest_visit to now
            self.request.session['visit_to_print'] = last_visit
            self.request.session['latest_visit'] = datetime.now()\
                .strftime("%b %d %Y %I:%M %p")
        else:
            # If user didn't visit before, create latest visit to now
            self.request.session['latest_visit'] = datetime.now()\
                .strftime("%b %d %Y %I:%M %p")
            self.request.session['visit_to_print'] = None

        context['visit'] = self.request.session['visit_to_print']
        return context


class MovieDetailView(DetailView):
    model = Movie
    queryset = Movie.active.all()
    template_name = 'movie/detail.html'
    context_object_name = 'movie'


class MovieCreateView(SuccessMessageMixin, CreateView):
    form_class = MoviePageForm
    success_url = reverse_lazy('movie:movie_list')
    template_name = 'movie/add_update_form.html'
    success_message = "%(title)s created successfully!"


class MovieUpdateView(SuccessMessageMixin, UpdateView):
    model = Movie
    queryset = Movie.active.all()
    form_class = MoviePageForm
    template_name = 'movie/add_update_form.html'
    success_message = '%(title)s updated successfully!'
    success_url = reverse_lazy('movie:movie_list')


class MovieSoftDeleteView(SingleObjectMixin, View):
    model = Movie

    def post(self, *args, **kwargs):
        movie = super(SoftDeleteView, self).get_object()
        movie.is_active = False
        movie.save()
        messages.success(self.request, movie.title + ' deleted successfully!')
        return HttpResponseRedirect(reverse('movie:movie_list'))


class MovieLikeView(SingleObjectMixin, View):
    model = Movie

    def get(self, *args, **kwargs):
        movie = Movie.objects.get(id=self.request.GET['movie_id'])
        movie.likes += 1
        movie.save()
        likes = movie.likes
        return HttpResponse(likes)
