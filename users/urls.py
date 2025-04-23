from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
     path("members/",
         views.members,
         name="members"),
     path("add_members/",
         views.add_members,
         name="add_member"),
     path("delete_members/<uuid:user_id>",
         views.delete_members,
         name="delete_member"),
     path("update_member/<uuid:user_id>",
         views.update_member,
         name="update_member"),
     path("member_profile/<uuid:user_id>",
         views.member_profile,
         name="member_profile"),
     path("create_member_profile/<uuid:user_id>",
         views.create_member_profile,
         name="add_member"),
     path("update_member_profile/<uuid:user_id>",
         views.update_member_profile,
         name="update_member"),
     path('user_with_profile/<uuid:user_id>/', 
          views.get_user_with_profile, 
          name="user_with_profile"),
     path("request-verification/", 
          views.request_email_verification,
          name="request-verification"),
     path("verify-email/", 
          views.verify_email,
          name="verify-email")
]
