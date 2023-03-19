from django.urls import path
from . import views
urlpatterns =[
  #user api
    path("api/v1.0/register/", views.RegisterUser, name="RegisterUser"),
    path("api/v1.0/get_all_user/", views.Get_all_users),
    path("api/v1.0/retrieve_pin/", views.Retrieve_pin, name="retrieve_pin"),
    path('api/v1.0/login/', views.C_Login.as_view()),
    #video api,
    path('api/v1.0/showvideo/', views.Show_video, name="video"),
    path("api/v1.0/delete_video/<int:id>/", views.Delete_video),
    path("api/v0.1/postvideo/", views.Postvideo.as_view()),
    #article api,
    path('api/v1.0/article/', views.Article_fun, name="article"),
    path("api/v1.0/update_article/<int:id>/", views.Update_article),#
    path('api/v1.0/cancel/', views.Api_Cancel),
    path('api/v1.0/add_user_to_mailing_list/', views.Add_user_to_mailing_list),
    path('api/v1.0/check_status/', views.Check_User_Status),
    path("staffing/", views.Make_user_admin ), #
    path("api/v1.0/create_session_api/", views.Create_checkout_session_api),  # Create_sub
    path("api/v1.0/create_session_api_test/", views.Create_checkout_session_api_test),  # Create_sub_test  
    #stripe configuration and website url
    path('', views.Home, name='home'),
    path('payment/', views.Stripe_config_pay),
    path('success/', views.success),
    path('cancel/', views.cancel),
    path('webhook/', views.stripe_webhook),
    path('webhook_test/', views.stripe_webhook_test),
    path("create-checkout-session/", views.Create_checkout_session, name="create_checkout_session"),
  
    path("webregister/", views.WebRegister, name='webregister' ),
    path("weblogin/", views.WebLogin, name='weblogin'),  
    path("weblogout/", views.WebLogout, name='weblogout'),  
    path("postvideo/", views.Webpost_video, name='postvideo'),
    path("postarticle/", views.Webpost_article, name='postarticle'), 
    path("showarticle/", views.Webdisplay_article, name='showarticle'), 
    path("showvideo/", views.Webdisplay_video, name='showvideo'), 
    path('retreivepin/', views.WebRetrieve_pin, name="retreivepin"),
    path('edith/<int:id>/', views.Webedith_article, name="Edith_article"),
    path('edith/<int:id>/update/', views.Webupdate_article, name="Update_article"),
    path('deletearticle/<int:id>/', views.Webdelete_article, name="Delete_article"),
    path('deletevideo/<int:id>/', views.Webdelete_video, name="Delete_video"),
    path('saving/', views.Saving, name="saving"),
    path('funnel/', views.Funnel, name="funnel"),
]  





