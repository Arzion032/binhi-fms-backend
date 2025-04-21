from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser, UserProfile
from .serializers import UserSerializer, UserProfileSerializer, UserWithProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
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