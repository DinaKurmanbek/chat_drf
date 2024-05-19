from django.contrib import admin

from chat.models import Chat, ChatSettings

# Register your models here.
admin.site.register(Chat)
admin.site.register(ChatSettings)