from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser, UserProfile, VerifiedEmail
from .serializers import UserSerializer, UserProfileSerializer, UserWithProfileSerializer, SignupSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import uuid
# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def members(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_members(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        """ 
        Another Option:
        return Response({
            "message": "User created successfully",
            "user": serializer.data,
            "user_id": serializer.data['id']
        }, status=status.HTTP_201_CREATED)
        
        """
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_member(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    serializer = UserSerializer(user, data=request.data, partial=True)  # partial=True makes PUT behave more like PATCH
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def delete_members(request,user_id):
    
    user= CustomUser.objects.get(id=user_id)
    user.delete()
    return Response({"message": f"User deleted successfully"})

@api_view(['POST'])
@permission_classes([AllowAny])
def update_members(request):
    
    user_id = request.data.get("id")
    user= CustomUser.objects.get(id=user_id)
    user.delete()
    return Response({"message": f"User deleted successfully"})

@api_view(['GET'])
@permission_classes([AllowAny])
def member_profile(request, user_id):
    user = get_object_or_404(UserProfile, user=user_id)
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_member_profile(request,user_id):
    user = get_object_or_404(CustomUser, id=user_id)  

    data = request.data.copy()
    data['user'] = user.id 

    serializer = UserProfileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_member_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        return Response({"error": "Profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(profile, data=request.data, partial=True)  # PATCH-like behavior with PUT

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_with_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    serializer = UserWithProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_email_verification(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)

        # generate fake token just for demo purposes
        token = str(uuid.uuid4())

        verification_link = f"http://localhost:8000/verify-email/?token={token}&email={email}"

        # in real world: store token and validate it later
        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Verification link sent!'}, status=200)
    except Exception as e:
        return Response({"error": {e}})
    
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    email = request.GET.get('email')
    # token = request.GET.get('token')  # add token checking here

    if not email:
        return Response({'error': 'Invalid request'}, status=400)

    # Save to VerifiedEmail table
    VerifiedEmail.objects.get_or_create(email=email)

    return Response({'message': 'Email verified successfully'}, status=200)