from django.conf import settings
from rest_framework import serializers
from .models import Tweet
from django import forms

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH

class TweetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['content']

    def validate_content(self, value):
        if len(value)>MAX_TWEET_LENGTH:
            raise forms.ValidationError("This tweet is too long")
        return value