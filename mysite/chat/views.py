from collections import OrderedDict
from venv import logger

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from rest_framework import generics, mixins, permissions, request
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response

from chat.permissions import DjangoModelPermissionsWithRead
from chat.models import Documents, Chat, Message, ChatSettings, ChatResponse
from chat.serializers import ChatSerializer, ChatWithChatSettingsSerializer, MessageSerializer, ChatResponseSerializer
from chat.serializers import ChatWithMessagesSerializer, UserSerializer

from rest_framework import status
from rest_framework.views import APIView

from .serializers import ChatSettingsSerializer, ChatSettingsCreateSerializer
from .utils import get_chatgpt_response, search_documents

# from blog.filters import PostFilter


chat_queryset = Chat.objects.order_by('id')  # Order by a unique field, such as 'id'
paginator = Paginator(chat_queryset, 5)


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer



from rest_framework import generics, permissions, filters
from .models import Chat, ChatSettings
from .serializers import ChatSerializer

class ChatListCreateView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'updated_at']
    search_fields = ['title']

    def perform_create(self, serializer):
        data = self.request.data.copy()
        chat_settings_data = data.pop('chat_settings', None)
        chat = serializer.save(user=self.request.user)

        if not chat.chat_settings.exists() and chat_settings_data:
            ChatSettings.objects.create(chat=chat, **chat_settings_data)

    def get_queryset(self):
        queryset = Chat.objects.filter(user_id=self.request.user.pk)
        queryset = self.filter_queryset(queryset)
        return queryset

    # def get_queryset(self):
    #     return Chat.objects.filter(user_id=self.request.user.pk)


class ChatRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Chat.objects.filter(user_id=self.request.user.pk)


class ChatSettingsView(generics.RetrieveUpdateAPIView):
    queryset = ChatSettings.objects.all()
    serializer_class = ChatSettingsSerializer

    def get_object(self):
        # Get the chat ID from the URL parameter
        chat_id = self.kwargs.get('pk')
        # Get the chat settings for the current user and chat
        chat_settings = ChatSettings.objects.get(chat_id=chat_id, chat__user=self.request.user)
        return chat_settings

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()



class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        chat_id = self.request.data.get('chat')
        print(chat_id, "test1")
        try:
            chat = Chat.objects.get(pk=chat_id, user=self.request.user)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat does not exist.'})

        serializer.save(chat=chat, status=1)

    def get_queryset(self):
        return Message.objects.filter(chat__user=self.request.user)


class MessageRetrieveCreateView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,

):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data["chat"] = kwargs.get("pk")
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        return Message.objects.filter(chat_id=self.kwargs.get("pk"))



class MessageRetrieveUpdateDeleteView(
    generics.GenericAPIView,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,

):
    #queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        print(self.kwargs.get("message_pk"))
        return Message.objects.get(chat_id=self.kwargs.get("pk"), id = self.kwargs.get("message_pk"))




class MessageResponseAPIView(generics.RetrieveAPIView):

    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        try:
            chat_id = self.kwargs.get("chat_id")
            message_id = self.kwargs.get("pk")
            message = Message.objects.get(chat_id=chat_id, id=message_id)
            question = message.text

            # Get the chat settings for the current chat
            chat_settings = ChatSettings.objects.get(chat_id=chat_id)
            print(chat_settings.response_length)

            related_content = search_documents(question)

            response = get_chatgpt_response(question, context=related_content, max_tokens=chat_settings.response_length)

            new_message = Message.objects.create(chat=message.chat, text=response,
                                                 status=2)  # Assuming status=1 means a question
            return new_message

        except Message.DoesNotExist:
            raise Http404("Message does not exist")

        except ValidationError as e:
            raise ValidationError("Failed to create a new message for the response")

