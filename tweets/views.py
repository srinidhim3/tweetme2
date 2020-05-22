from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from .models import Tweet
import random
from .forms import TweetForm
from .serializers import TweetSerializers, TweetActionSerializer, TweetCreateSerializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
#@authentication_classes([SessionAuthentication])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetCreateSerializers(data = request.POST or None)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user = request.user) 
        return Response(serializer.data, status = 201)
    return Response({}, status = 400)

@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializers(qs, many = True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    serailizer = TweetActionSerializer(data=request.data)
    if serailizer.is_valid(raise_exception=True):
        data = serailizer.validated_data
        tweet_id = data.get('id')
        action = data.get('action')
        content = data.get('content')
        qs = Tweet.objects.filter(id = tweet_id)
        if not qs.exists():
            return Response({}, status = 404)
        obj = qs.first()
        if action == 'like': 
            obj.likes.add(request.user)
            serailizer = TweetSerializers(obj)
            return Response(serailizer.data, status=200)
        elif action == 'unlike':
            obj.likes.remove(request.user)
            serailizer = TweetSerializers(obj)
            return Response(serailizer.data, status=200)
        elif action == 'retweet':
            new_tweet = Tweet.objects.create(user=request.user, parent=obj, content=content)
            serailizer = TweetSerializers(new_tweet)
            return Response(serailizer.data, status=201)
    return Response({}, status = 401)

@api_view(['delete', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id = tweet_id)
    if not qs.exists():
        return Response({'error':'could not be found'}, status = 404)
    qs = qs.filter(user = request.user)
    if not qs.exists():
        return Response({'message': 'you cannot delete this tweet'}, status = 401)
    obj = qs.first()
    obj.delete()
    return Response({'message': 'Tweet removed'}, status = 200)

@api_view(['GET'])
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id = tweet_id)
    if not qs.exists():
        return Response({}, status = 404)
    obj = qs.first()
    serializer = TweetSerializers(obj)
    return Response(serializer.data)


def tweet_create_view_pure_django(request, *args, **kwargs):
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status = 401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get("next") or None
    if form.is_valid():
        obj = form.save(commit = False)
        obj.user = user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status = 201)
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={"form":form})

def tweet_list_view_pure_django(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]
    data = {
        "response": tweets_list
    }
    return JsonResponse(data)

def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={},status=200)

def tweet_detail_view_pure_django(request, tweet_id ,*args, **kwargs):
    data = {
        "id": tweet_id,
    }
    status = 200
    try:
        obj = Tweet.objects.get(id = tweet_id)
        data["content"] = obj.content
    except:
        data["message"]= "Not Found"
        status = 404
        print(data, status)
    return JsonResponse(data, status=status)
    