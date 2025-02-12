from django.contrib import admin
from django.urls import path,include
from .views import RegisterView,UserLoginView,UserLogoutView,activate,MoreInfoDetailUpdateView,UserDeleteView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register' ),
    path('login/', UserLoginView.as_view(), name='login' ),
    path('logout/', UserLogoutView.as_view(), name='logout' ),
    path('register/', RegisterView.as_view(), name='register' ),
    path('active/<uid64>/<token>/',activate ),
    path('user/<str:username>/', MoreInfoDetailUpdateView.as_view(), name='moreinfo-detail-update'),
    path('user/delete/<str:username>/', UserDeleteView.as_view(), name='user-delete'),
]
