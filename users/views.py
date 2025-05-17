from .models import CustomUser, UserProfile, VerifiedEmail
from .serializers import UserSerializer, UserProfileSerializer, UserWithProfileSerializer, SignupSerializer, CustomTokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomTokenObtainPairSerializer
import uuid


# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def members(request):
    users = CustomUser.objects.filter(is_approved=True, is_active=True)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def pending_members(request):
    """
    Pending members
    """
    pending_users = CustomUser.objects.filter(
        is_rejected=False,
        is_approved=False,
        is_active=False
    )
    
    serializer = UserSerializer(pending_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def rejected_members(request):
    """
    Rejected members
    """
    rejected_users = CustomUser.objects.filter(
        is_rejected=True,
        is_approved=False,
        is_active=False
    )
    serializer = UserSerializer(rejected_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_members(request):
    
    user = request.data.copy()
    user['is_approved'] = True
    user['is_active'] = True
    user['is_rejected'] = False
    
    serializer = UserSerializer(data=user)
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
@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_member(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
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
    email = request.data.get('email')

    # Validate email is present
    if not email:
        return Response({'error': 'Email is required'}, status=400)

    # Validate format
    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Invalid email format"}, status=400)

    # Check if email already verified
    if VerifiedEmail.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=409)

    try:
        # Generate and send verification token
        token = str(uuid.uuid4())  # Demo token, not stored

        verification_link = f"http://localhost:8000/users/verify-email/?token={token}&email={email}"

        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Verification link sent!'}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

    
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


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    email = request.data.get('email')

    # 1. Check if email is valid
    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Invalid email format"}, status=400)

    # 2. Check if email is verified
    if not VerifiedEmail.objects.filter(email=email).exists():
        return Response({"error": "Email is not verified."}, status=status.HTTP_403_FORBIDDEN)
    
    # 3. Validate user data
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # 4. Create user with proper password hashing
        user = CustomUser.objects.create_user(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username'],
            contact_no=serializer.validated_data['contact_no'],
            role=serializer.validated_data['role'],
            password=request.data.get('password')  # This will be hashed by create_user
        )
        
        # 5. Return serialized user without password
        user_data = UserSerializer(user).data
        return Response({
            "message": "User created successfully",
            "user": user_data,
            "user_id": user_data['id']
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"error": "Invalid credentials. Please check your email and password."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception:
            return Response(
                {"error": "Invalid credentials. Please check your email and password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "You have access to this protected view!",
            "user_email": request.user.email,
            "user_id": str(request.user.id)
        })
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([AllowAny])
def accept_member(request, user_id):
    
    try: 
        user = get_object_or_404(CustomUser, id=user_id)

        user.is_approved = True
        user.is_active = True
        user.is_rejected = False

        user.save()
        
        return Response({"message" : f"User {user.username} approved successfully."})
    
    except Exception as e:
        return Response({"error":{e}}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def reject_member(request, user_id):
    
    try: 
        user = get_object_or_404(CustomUser, id=user_id)

        user.is_rejected = True
        user.is_approved = False
        user.is_active = False

        user.save()
        
        return Response({"message" : f"User {user.username} has been declined."})
    
    except Exception as e:
        return Response({"error":{e}}, status=status.HTTP_400_BAD_REQUEST)

