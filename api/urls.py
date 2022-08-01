from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login),
    path('register', views.register),
    path('create-restaurant',views.createRestaurant),
    path('create-menu',views.createMenu),
    path('menus',views.getMenus),
    path('vote',views.voteForMenu),
    path('result',views.getResults),

]
