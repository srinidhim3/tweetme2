from django.conf import settings
from rest_framework import serializers
from .models import Tweet
from django import forms

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTION_OPTIONS = settings.TWEET_ACTION_OPTIONS

class TweetActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    content = serializers.CharField(allow_blank=True, required=False)

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError("This is not a valid action for tweets")
        return value
class TweetCreateSerializers(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tweet
        fields = ['id','content','likes']

    def get_likes(self, obj):
        return obj.likes.count()

    def validate_content(self, value):
        if len(value)>MAX_TWEET_LENGTH:
            raise forms.ValidationError("This tweet is too long")
        return value

class TweetSerializers(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    parent = TweetCreateSerializers(read_only=True)
    class Meta:
        model = Tweet
        fields = ['id','content','likes','is_retweet', 'parent'] 

    def get_likes(self, obj):
        return obj.likes.count()

    def get_content(self, obj):
        content = obj.content
        if obj.is_retweet:
            content = obj.parent.content
        return content
