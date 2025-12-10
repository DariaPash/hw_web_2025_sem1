
from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question_view, name='question'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('ask/', views.ask, name='ask'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]