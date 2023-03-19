from rest_framework import serializers
from .models import CustomUser, Article, Video, Newsletter_users
#from models import Subscription, UserProfile from .appserializers import  UserSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['pk', 'email', 'first_name', "is_staff", 'username',
                  'last_name',  'pin', 'is_subscription_active', 'subscription_type']
        


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title','content', ]



class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title','video', 'author' ]  


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter_users
        fields = ['id', 'name','email' ]  

