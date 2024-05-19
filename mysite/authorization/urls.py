from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authorization import views

urlpatterns = [
    path('register/', views.RegistrationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('personal-area/', views.PersonalAreaView.as_view(), name='personal_area'),
]
