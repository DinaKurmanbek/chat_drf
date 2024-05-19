
from django.urls import path

from chat import views

from chat.views import UserListCreateAPIView

from django.urls import path



urlpatterns = [
    path('', views.ChatListCreateView.as_view()),
    path('<int:pk>/', views.ChatRetrieveUpdateDestroyView.as_view()),

    path('messages/', views.MessageListCreateView.as_view()),
    path('<int:pk>/messages/', views.MessageRetrieveCreateView.as_view()),
    path('<int:pk>/messages/<int:message_pk>/', views.MessageRetrieveUpdateDeleteView.as_view()),

    path('<int:pk>/settings/', views.ChatSettingsView.as_view()),
    #path('chat/<int:chat_id>/settings/', ChatSettingsListCreateView.as_view(), name='chat-settings-create'),

    path('users/', UserListCreateAPIView.as_view(), name='user_list_create'),

    #path('<int:pk>/messages/<int:message_pk>/response/', views.MessageResponseAPIView.as_view()),
    path('<int:chat_id>/messages/<int:pk>/response/', views.MessageResponseAPIView.as_view()),

]
