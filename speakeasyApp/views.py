from email import message
import email
from django.shortcuts import render,redirect
from django.http.response import JsonResponse, HttpResponse 
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError



#import for background schuduler
import threading
import schedule

#Time and date module
import datetime
from datetime import date, timedelta
import time

#stripe for payment and subscription
import stripe

#django send mail module
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import json
# self define Module
from .appserializers import UserSerializer, ArticleSerializer, VideoSerializer
from .models import CustomUser, Video, Article, Newsletter_users
from .form import VideoForm
from speakeasy.settings import EMAIL_HOST_USER
from django.views.generic import TemplateView
from django.conf import settings

#it return home page on web
def Home(request):
    
    if "user" in request.session:
        user = request.session["user"]
        first_name = user.get("first_name")

        context =  {
            "first_name" : first_name,
            "is_staff" : user["is_staff"]
        }
        return render(request, "home.html", context)
    else:
        return render(request, "home.html")


def Webpost_video(request):

    return render(request, 'email_template.html')

#Post_video   Post_article


def Webdisplay_video(request):
    video = Video.objects.all()
    context = {
        'video': video,
    }
    return render(request, 'show_video.html', {"video": video})


def Webdelete_video(request, id):
    video_method = Video.objects.get(id=id)
    data = video_method.video.delete()
    if data is None:
        return redirect('/showvideo')
    return render(request, 'show_video.html')


def Webpost_article(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        data = Article(title=title, content=content)
        data.save()
        return redirect('/showarticle')
    return render(request, 'post_article.html')


def Webdisplay_article(request):
    posts = Article.objects.all()
    context = {
        'articles': posts,
    }
    return render(request, 'show_article.html', context)


def Webdelete_article(request, id):
    article = Article.objects.filter(id=id)
    article.delete()
    return render(request, 'show_article.html')


def Webedith_article(request, id):
    qry = Article.objects.get(id=id)
    print(qry.content, " and", qry.title)
    return render(request, "edith_article.html", {"title": qry.title, "content": qry.content})


def Webupdate_article(request, id):
    qry = Article.objects.get(id=id)
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        qry.title = title
        qry.content = content
        qry.save()
        posts = Article.objects.all()
        context = {
            'articles': posts,
        }
    return render(request, 'show_article.html', context)
############################################################
#funtion that handle login on web
##############################################################
def WebLogin(request):
    if request.method == "POST":
        pin = request.POST.get("pin")
        email = request.POST.get("email")    
        try:
            user = CustomUser.objects.get(email=email)
            if (email == user.email) and (pin == user.pin):
                context = {
                    "pk": user.pk,
                    "email":  user.email,
                    "first_name": user.first_name,
                    "is_staff" : user.is_staff
                }
                request.session['user'] = context
                return redirect("/")
            else:
                context = {
                    "message" : "Wrong Email Or Pin"
                }
                return render(request, "login.html", context=context)

        except CustomUser.DoesNotExist:
            
            context = {
                "message" : "User Does Not Exist"
            }
            return render(request, "login.html", context=context)
            
                 
    return render(request, "login.html")

#function that handle logout
def WebLogout(request):
    if request.session:
        del request.session['user']

        return redirect("/weblogin")
    return redirect("/weblogin")


def WebRegister(request):
    data = CustomUser()
    if request.method == "POST":
        qry = request.POST.get("first_name")
        data.first_name = request.POST.get("first_name")
        data.last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        data.pin = request.POST.get("pin")
        current_time = datetime.datetime.now()
        current = str(current_time.strftime('%Y%m%d%H%M'))
        username = str(qry) + str(current)
        data.username = username
        data.email = email
        
        try:
            user = CustomUser.objects.get(email = email)
            if user:
                context = {
                    "email": user.email+" "+" Already Exist"
                }
                return render(request, "register.html", context=context)
            else:
                data.save()
            return render(request, "login.html")
        except :
            data.save()
            return render(request, "login.html" )
    return render(request, "register.html", {})




def Saving(request):
    return render(request, 'saving.html')


def Funnel(request):
    return render(request, 'funnel.html')

def WebRetrieve_pin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            content = {
                'user': user.first_name,
                'message': 'Your pin has been retrieved successful, your pin is: '+ user.pin
            }
            send_to = user.email
            send_from = EMAIL_HOST_USER
            subject = "Pin Rest"
            message = get_template('email_template.html').render(content)
            msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
            )
            msg.content_subtype = "html"
            msg.send()
            context = {"message" : "Check your Email for your Pin" }
            return redirect("weblogin")
        except:


            context = {
                'message': 'Email does not exist'
            }
        return render(request, "retreve_pin.html", context=context)
    

    return render(request, 'retreve_pin.html')

@csrf_exempt
def Stripe_config_pay(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def Create_checkout_session(request):
    if request.method == 'GET':
        domain_url ="https://speakeasyandpurge-eovuo.ondigitalocean.app/"
        #domain_url_test = https: // speakeasyandpurge-eovuo.ondigitalocean.app/test_webhook/
        local_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url+'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url+'cancel/',
                payment_method_types=['card'],
                mode= 'subscription', #'payment'
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,# #STRIPE_ONE_TIME_PAYMENT_ID, 
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})



#@login_required
def success(request):
    return render(request, 'success.html')


#@login_required
def cancel(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    

    return render(request, 'cancel.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Api_Cancel(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    email = request.data.get('email')

    user = CustomUser.objects.get(email=email)
    subscription_id = user.stripeSubscriptionId
    #data = stripe.Subscription.retrieve(subscription_id)
    #is_subscription_active = data['plan']['active']

    if (user.subscription_type == "subscription"):
        try:
            #Modify was use instead of delete, the reason being that,the subscription will be active till the 
            #the current subcription expired. and customer will not be charge again.
            data = stripe.Subscription.modify(subscription_id)
            user.is_subscription_active = False
            user.save()
            #send mail to user for successful subscription
            content = {
                'user': user.first_name,
                'message': '''You have Unsubscribe for Speakeasy 
                                        and Purge Service 
                                        You will not be able to access some services'''
            }
            send_to = email
            send_from = EMAIL_HOST_USER
            subject = "Cancel subscription"
            message = get_template('email_template.html').render(content)
            msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
            )
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            return Response({
                        'message': "You have successfuly cancelled your subscription",
                        'is_subscription_active': False,
                        "subscription_type": user.subscription_type,
                        'status': status.HTTP_200_OK
                        })
        except:
            message = {
                "message" : " subscription is not active!",
                status:301
            }
            return Response(message, status=301) 
        
    else:
        message = {
                "message" : " subscription does not exist on this account!",
                status: 301
            }
        return Response(message, status=400)

  ###################################################################################
  # test checkout session
  # #################################################################################  

@api_view(['POST', 'GET'])
def Create_checkout_session_api_test(request):
    if request.method == 'POST':
        domain_url ="https://speakeasyandpurge-eovuo.ondigitalocean.app/"
        local_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
        payment_type = request.data.get("payment_type")
        if payment_type == 'subscription' :
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url+'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url+'cancel/',
                    payment_method_types=['card'],
                    mode='subscription', 
                    line_items=[
                        {
                            'price': settings.STRIPE_PRICE_ID_TEST,
                            'quantity': 1,
                        }
                    ]
                )
                return Response({'sessionId': checkout_session['id']}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'error': str(e)})
        elif payment_type == 'payment' :
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url +
                    'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url+'cancel/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[
                        {
                            'price': settings.STRIPE_ONE_TIME_PAYMENT_ID_TEST,
                            'quantity': 1,
                        }
                    ]
                )
                return Response({'sessionId': checkout_session['id']}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return Response({"message": "Wrong payment_type"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST', 'GET'])
def Create_checkout_session_api(request):
    if request.method == 'POST':
        domain_url ="https://speakeasyandpurge-eovuo.ondigitalocean.app/"
        local_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_type = request.data.get("payment_type")
        if payment_type == 'subscription' :
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url+'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url+'cancel/',
                    payment_method_types=['card'],
                    mode='subscription', 
                    line_items=[
                        {
                            'price': settings.STRIPE_PRICE_ID,
                            'quantity': 1,
                        }
                    ]
                )
                return Response({'sessionId': checkout_session['id']}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'error': str(e)})
        elif payment_type == 'payment' :
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=request.user.id if request.user.is_authenticated else None,
                    success_url=domain_url +
                    'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url+'cancel/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[
                        {
                            'price': settings.STRIPE_ONE_TIME_PAYMENT_ID,
                            'quantity': 1,
                        }
                    ]
                )
                return Response({'sessionId': checkout_session['id']}, status=status.HTTP_200_OK)
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return Response({"message": "Wrong payment_type"}, status=status.HTTP_400_BAD_REQUEST)

 #stripe Webhook that handle subscription
@csrf_exempt
def stripe_webhook_test(request):
    event = None
    today = datetime.date.today()
    expiring_date = today + timedelta(days=30)
    payload = request.body.decode('utf-8')
    out_put = json.loads(payload)
    checkout_session = out_put['type']
    event = out_put['data']['object']

    if checkout_session == "checkout.session.completed":
        email = event['customer_details']['email']
        subscription_type = event['mode']
        stripe_subscription_id = event.get('subscription', "")
        stripe_customer_id = event.get('customer')
        user = CustomUser.objects.get(email=email)
        #update user subscription to be  active
        user.is_subscription_active = True
        user.date_subscribed = today
        user.stripeSubscriptionId  = stripe_subscription_id
        user.stripeCustomerId = stripe_customer_id
        user.subscription_type = subscription_type
        user.save()
        #send mail to user for successful subscription
        content = {
                'user': user.first_name,
                'message': '''Your subscription was successful.
                                Login to get started using the app. 
                                Your subscription will expire on: '''+str(expiring_date)
                } #
        send_to = email
        send_from = EMAIL_HOST_USER
        subject = "Subscription Successful"
        message = get_template('email_template.html').render(content)
        msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        return Response(status= status.HTTP_200_OK)
    
    return HttpResponse(status=200)           

#stripe Webhook that handle subscription
@csrf_exempt
def stripe_webhook(request):
    event = None
    today = datetime.date.today()
    expiring_date = today + timedelta(days=30)
    payload = request.body.decode('utf-8')
    out_put = json.loads(payload)
    checkout_session = out_put['type']
    event = out_put['data']['object']

    if checkout_session == "checkout.session.completed":
        email = event['customer_details']['email']
        subscription_type = event['mode']
        stripe_subscription_id = event.get('subscription', "")
        stripe_customer_id = event.get('customer')
        user = CustomUser.objects.get(email=email)
        #update user subscription to be  active
        user.is_subscription_active = True
        user.date_subscribed = today
        user.stripeSubscriptionId  = stripe_subscription_id
        user.stripeCustomerId = stripe_customer_id
        user.subscription_type = subscription_type
        user.save()
        #send mail to user for successful subscription
        content = {
                'user': user.first_name,
                'message': '''Your subscription was successful.
                                Login to get started using the app. 
                                Your subscription will expire on: '''+str(expiring_date)
                } #
        send_to = email
        send_from = EMAIL_HOST_USER
        subject = "Subscription Successful"
        message = get_template('email_template.html').render(content)
        msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        return Response(status= status.HTTP_200_OK)
    
    return HttpResponse(status=200)



@api_view(['GET', 'POST'])
def Newsletter(request):
    if request.method == "POST":
        subscribe_user = Newsletter_users()
        subscribe_user.email = request.data.get('email')
        subscribe_user.name = request.data.get('name')
        subscribe_user.save()
        data = {
            "message" : "Successfully Added to Newsletter Subscribers"
        }
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({"message" : "Not successful"}, status=status.HTTP_400_BAD_REQUEST)


def Get_newsletter_subscribers():
    email = Newsletter_users.objects.all().values_list('email', flat=True)
    return email



@api_view(['GET', 'POST'])
def Add_user_to_mailing_list(request):
    if request.method == "POST":
        email = request.data['email']
        name = request.data['name']
        api_key = settings.MAILCHIMP_API_KEY
        data_center = settings.MAILCHIMP_DATA_CENTER
        list_id = settings.MAILCHIMP_EMAIL_LIST_ID
        mailchimp = Client()
        mailchimp.set_config({
            "api_key": api_key,
            "server": data_center,
            
        })
        member_info = {
            "email_address": email,
            "status": "subscribed",
            'merge_fields': {
                "NAME": name,
            }
        }
        try:
            data = mailchimp.lists.add_list_member(list_id, member_info)
            return Response(data, status=status.HTTP_200_OK)
        except ApiClientError as error:
            return Response(format(error.text), status=status.HTTP_200_OK)
           


@api_view(['GET', 'POST'])
def Article_fun(request):
    if request.method == "GET":
        article = Article.objects.all()
        articles = ArticleSerializer(article, many=True)
        return Response(articles.data, status= status.HTTP_200_OK)
    elif request.method == "POST":
        article = ArticleSerializer(data=request.data)
        if article.is_valid():
            article.save()
            email  = Get_newsletter_subscribers()
            content = {
                'message': request.data.get('content')
                              
            }
            send_to = email
            send_from = EMAIL_HOST_USER
            subject = request.data.get('title')
            message = get_template('email_template.html').render(content)
            msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
            )
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            return Response(article.data, status=status.HTTP_200_OK)
        return Response(article.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def Update_article(request, id):
    if request.method == "GET":
        try:
            article = Article.objects.filter(id=id)
            article = ArticleSerializer(article, many=True)
            return Response(article.data, status= status.HTTP_200_OK)
        except:
            error= {
                "message" : "Article does not exist"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PUT":
        try:
            article = Article.objects.get(id=id)
            title = request.data.get('title', article.title)
            content = request.data.get('content', article.content)
            article.title = title
            article.content = content
            article.save()
            data = {
                'message': "Updated successfully",
            }
            return Response(data, status=status.HTTP_200_OK)
        except:
            error = {
                "message": "Article does not exist"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        try:
            article = Article.objects.get(id=id)
            article.delete()
            data = {
                'message': "Deleted successfully",
            }
            return Response(data, status=status.HTTP_200_OK)
        except:
            error = {
                "message": "Article does not exist"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

#diplay Video for API
@api_view(['GET'])
def  Show_video(request):
    if request.method == "GET":
        video = Video.objects.all()
        videos = VideoSerializer(video, many=True)
        return Response(videos.data, status= status.HTTP_200_OK)
    return Response( status= status.HTTP_400_BAD_REQUEST)



#delete Video for API
@api_view(['DELETE'])
def  Delete_video(request, id):
    if request.method == "DELETE":
        try:
            video = Video.objects.filter(id=id)
            video.delete()
            videos = VideoSerializer(video, many=True)
            return Response(videos.data, status= status.HTTP_200_OK)
        except:
            error = {
                "message": "Article does not exist"
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

#post video
class Postvideo(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        product = VideoSerializer(data=request.data)
        if product.is_valid():
            product.save()
            return Response(product.data, status=status.HTTP_200_OK)
        return Response(product.errors, status=status.HTTP_400_BAD_REQUEST)



#RETRIEVE PIN FOR API AND SEND IT VIA MAIL
@api_view(['POST'])
def Retrieve_pin(request):
    email = request.data.get('email')
    try:
        user = CustomUser.objects.get(email=email)
        if user:
            content = {
            'user': user.first_name,
            'message' : 'Your pin was been retrieved successfully. Your pin is: '+user.pin
            }
            send_to = user.email
            send_from = EMAIL_HOST_USER
            subject = "Pin Rest"
            message = get_template('email_template.html').render(content)
            msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
            )
            msg.content_subtype = "html" 
            msg.send(fail_silently=False)

            return Response({'status' : status.HTTP_200_OK})
        else:
            return Response({
                'error_message': "Invalid Pin or Email", 
                'status ' : status.HTTP_400_BAD_REQUEST
                
            })
    except:
        return Response({ 
            'error_message': "User Does Not exist" ,
            'status' : status.HTTP_400_BAD_REQUEST
            })


#the class that will handle login and generate token for user
class C_Login(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        today = datetime.date.today()                             
        email = request.data.get('email')
        pin = request.data.get('pin')
        try:
            user = CustomUser.objects.get(email=email)
            if (user.email == email) and (user.pin == pin): 
                token, created = Token.objects.get_or_create(user=user)
                if (user.subscription_type == "subscription") and (user.is_subscription_active is True):
                    return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'email': user.email,
                    'name' : user.last_name + "  " + user.first_name,
                    'is_subscription_active' : user.is_subscription_active,
                    "subscription_type" : user.subscription_type,
                    'message' : "Login Successful",
                    'status' : status.HTTP_200_OK

                    })

                elif (user.date_subscribed == None) or (user.date_subscribed.strftime('%Y%m%d') < today.strftime('%Y%m%d')):
                    return Response({
                        'token': token.key,
                        'email': user.email,
                        'name' : user.last_name + " " + user.first_name,
                        'is_subscription_active' : False,
                        'message' : "subscription is due",
                         "subscription_type" : user.subscription_type,
                        'status' : status.HTTP_200_OK
                       

                    })
                else:

                    return Response({
                        'token': token.key,
                        'user_id': user.pk,
                        'email': user.email,
                        'name' : user.last_name +"  " + user.first_name,
                        'is_subscription_active' : user.is_subscription_active,
                         "subscription_type" : user.subscription_type,
                        'message' : "Login Successful",
                        'status' : status.HTTP_200_OK

                    })
                
            else:
                
                return Response({
                    'error_message': "Invalid Pin or Email", 
                    'status ' : status.HTTP_400_BAD_REQUEST
                    
                })
        except:
            return Response({ 
                'error_message': "User Does Not exist" ,
                'status' : status.HTTP_400_BAD_REQUEST
                })



#the function that will handle user registration for API
@api_view(["POST"])
def RegisterUser(request):
    if request.method == "POST":
        user = request.data
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        pin = request.data.get('pin')
        current_time = datetime.datetime.now()
        username = first_name+str(current_time.strftime('%Y%m%d%H%M'))
        data = {
            "first_name" :  first_name,
            "last_name" : last_name,
            "email" :  email,
            "pin"   :  pin,
            "username" : username
        }
        register = UserSerializer(data=data)
        if register.is_valid():
            register.save()
            content = {
            'user': first_name,
            'message' : 'Congratulations! Your registration was Successful. Login to subscribe and start using the App'
            }
            send_to = email
            send_from = EMAIL_HOST_USER
            subject = "Registraton Successful"
            message = get_template('email_template.html').render(content)
            msg = EmailMessage(
                subject,
                message,
                send_from,
                [send_to],
            )
            msg.content_subtype = "html" 
            msg.send(fail_silently=False)
            return Response(register.data, status= status.HTTP_200_OK)
    return Response(register.errors, status= status.HTTP_400_BAD_REQUEST)



    

#For Admin to make user staff for ADMIN only

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def Make_user_admin(request):
    if request.method == "POST":
        email = request.data.get('email')
        user = CustomUser.objects.get(email=email)
        user.is_staff = True
        user.save()
    return Response(status=status.HTTP_200_OK)

#get all the users for Admin only
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Get_all_users(request):
    if request.method == "GET":
        users = CustomUser.objects.all()

        users = VideoSerializer(users, many=True)
        return Response(users.data, status=status.HTTP_200_OK)
    return Response(users.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def Check_User_Status (request):
    today = datetime.date.today()   
    email = request.data['email']
    try:
        user = CustomUser.objects.get(email=email)
        if (user.subscription_type == "subscription") and (user.is_subscription_active is True):
            return Response({
            'email': user.email,
            'name': user.last_name + "  " + user.first_name,
            'is_subscription_active': user.is_subscription_active,
            "subscription_type": user.subscription_type,
            'message': "Login Successful",
            'status': status.HTTP_200_OK

            })

        elif (user.date_subscribed == None) or (user.date_subscribed.strftime('%Y%m%d') < today.strftime('%Y%m%d')):
            return Response({
                'email': user.email,
                'name': user.last_name + " " + user.first_name,
                'is_subscription_active': False,
                'message': "subscription is due",
                "subscription_type": user.subscription_type,
                'status': status.HTTP_200_OK


            })
        else:

            return Response({
                'email': user.email,
                'name': user.last_name + "  " + user.first_name,
                'is_subscription_active': user.is_subscription_active,
                "subscription_type": user.subscription_type,
                'message': "Login Successful",
                'status': status.HTTP_200_OK

            })


    except:
        return Response({ 
            'error_message': "User Does Not exist" ,
            'status' : status.HTTP_400_BAD_REQUEST
            })

    


    
def run_continuously(interval=24):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def Check_due_subscribed_users():
    today = date.today()
    start_date = today - timedelta(days=30)
    end_date = today - timedelta(days=27)
    due_subscribers = CustomUser.objects.filter(
        date_subscribed__range=[start_date, end_date]
    ).values_list('email', flat=True)
    if due_subscribers:
        print(due_subscribers)
        content = {

            'message': 'Your subscription will expire Soon '
        }

        send_from = EMAIL_HOST_USER
        subject = "Reminder"
        message = get_template('email_template.html').render(content)
        msg = EmailMessage(
            subject,
            message,
            send_from,
            due_subscribers,
        )
        msg.content_subtype = "html" 
        #msg.send(fail_silently=False)
        return Response(status=status.HTTP_200_OK)
    else:
        print("no due subscribers")

    return Response(status=status.HTTP_200_OK)


#schedule.every().second.do(Check_due_subscribed_users)

# Start the background thread
#stop_run_continuously = run_continuously()
#24 hours = 8640
# Do some other things...
#time.sleep(8640)


