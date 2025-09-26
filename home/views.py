# home/views.py (functional-based views)
import random
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Users
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, UpdateProfileSerializer
)

# ----------------------
# SIGN UP
# ----------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# SIGN IN
# ----------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signin(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# SIGN OUT
# ----------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def signout(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"error": "refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Signed out successfully"})
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# GET CURRENT USER
# ----------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ----------------------
# UPDATE PROFILE
# ----------------------
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile(request):
    user = request.user
    serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------
# UPDATE PASSWORD
# ----------------------
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    return Response({"message": "Password updated successfully"})


# ----------------------
# RESET PASSWORD (GENERATE OTP)
# ----------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = Users.objects.get(email=email)
    except Users.DoesNotExist:
        return Response({"error": "No user with that email"}, status=status.HTTP_404_NOT_FOUND)

    otp = random.randint(100000, 999999)
    user.otp = otp
    user.otp_timestamp = timezone.now()
    user.save()

    # In real use: send OTP via email/SMS
    return Response({"message": "OTP generated. Use for verification.", "otp": otp})


# ----------------------
# VERIFY EMAIL (OTP)
# ----------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    if not email or not otp:
        return Response({"error": "email and otp required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = Users.objects.get(email=email, otp=otp)
    except Users.DoesNotExist:
        return Response({"error": "Invalid otp or email"}, status=status.HTTP_400_BAD_REQUEST)

    user.otp = None
    user.otp_timestamp = None
    user.save()
    return Response({"message": "OTP verified"})
