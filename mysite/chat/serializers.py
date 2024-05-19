from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Message, Chat, ChatSettings, ChatResponse


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ['pk', 'username']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


# class ChatSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#     created_at = serializers.DateTimeField(read_only=True)
#     updated_at = serializers.DateTimeField(read_only=True)
#
#     class Meta:
#         model = Chat
#         fields = ['title', 'user', 'chat_settings', 'created_at', 'updated_at']  # Assuming you want all these fields

class ChatSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSettings
        fields = ['id','response_length']


class ChatSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    chat_settings = ChatSettingsSerializer(required=False, read_only=True)  # Make chat_settings optional

    class Meta:
        model = Chat
        fields = ['title', 'user', 'created_at', 'updated_at', 'chat_settings']

    def create(self, validated_data):
        chat_settings_data = validated_data.pop('chat_settings', None)
        chat = Chat.objects.create(**validated_data)
        if chat_settings_data:
            ChatSettings.objects.create(chat=chat, **chat_settings_data)
        return chat




class MessageSerializer(serializers.ModelSerializer):
    #user = UserSerializer(read_only=True)
    #created_at = serializers.DateTimeField(read_only=True)
    #updated_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Message
        fields = ['text','chat', ]  # 'status', 'created_at', 'updated_at'


class ChatWithMessagesSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    class Meta:
        model = Chat
        fields = ['messages']


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['question', 'answer']  # 'status', 'created_at', 'updated_at'


class ChatWithResponsesSerializer(serializers.ModelSerializer):
    question = MessageSerializer(source='messages', many=True)
    response = ResponseSerializer(source='responses', many=True)
    class Meta:
        model = Chat
        fields = ['question', 'response']




class ChatWithChatSettingsSerializer(serializers.ModelSerializer):
    chat_settings = ChatSettingsSerializer()
    class Meta:
        model = Chat
        fields = ['chat_settings']


class ChatSettingsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSettings
        fields = ['response_length']


class ChatResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatResponse
        fields = ['question', 'answer']  # Add all fields that are relevant



