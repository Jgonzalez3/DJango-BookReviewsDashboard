from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^books$', views.books),
    url(r'^books/add$', views.booksadd),
    url(r'^books/(?P<bid>\d+)$', views.showbook, name="show_book"),
    url(r'^addbook$', views.addbook),
    url(r'^addreview$', views.addreview),
    url(r'^delete$', views.delete),
    url(r'^users/(?P<uid>\d+)$', views.showuser, name="show_user"),
    ]