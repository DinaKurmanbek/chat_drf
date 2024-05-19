from datetime import time

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from .utils import get_chatgpt_response, search_documents


class Documents(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    def __str__(self):
        return self.title

class Chat(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # verbose_name="Время обновления",


class Message(models.Model):
    text = models.TextField()
    STATUS_CHOICES = [
        (1,'Question') , (2, 'Answer')
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default = 1)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)  #verbose_name="Время обновления",
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', default = None)

    def __str__(self):
        return f"{self.text} ({self.pk})"

class ChatSettings(models.Model):
    # question = models.ForeignKey(Question, related_name='chat_settings', on_delete=models.CASCADE, default = None)
    response_length = models.IntegerField(default=100)  # Default response length
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_settings', default = None)
    # chat = models.OneToOneRel(Chat, on_delete=models.CASCADE, related_name='chat_settings')

    def __str__(self):
        return f"{self.chat}'s chat settings"


class ChatResponse(models.Model):
    question = models.ForeignKey(Message, related_name='responses', on_delete=models.CASCADE, default=None)
    settings = models.ForeignKey(ChatSettings, on_delete=models.CASCADE, default=None)
    answer = models.TextField()

    def __str__(self):
        return self.answer[:50]

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new instance
            # Generate the answer using the question text

            question_text = self.question.text
            max_length = self.settings.response_length
            related_content = search_documents(question_text)

            self.answer = get_chatgpt_response(question_text, context=related_content, max_tokens=max_length)
        super().save(*args, **kwargs)



# class UserFeedback(models.Model):
#     RATING_CHOICES = [
#         (1, 'Poor'),
#         (2, 'Fair'),
#         (3, 'Average'),
#         (4, 'Good'),
#         (5, 'Excellent')
#     ]
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     chat_response = models.ForeignKey(Message, null=True, on_delete=models.SET_NULL, default=None)  # Allow null if feedback is not for a specific response
#     rating = models.IntegerField(choices=RATING_CHOICES)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)  # verbose_name="Время обновления",
#     def __str__(self):
#         response_id = self.chat_response.id if self.chat_response else 'No specific response'
#         return f"Feedback by {self.user.username} on response {response_id}"








