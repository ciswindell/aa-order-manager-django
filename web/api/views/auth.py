"""Authentication views."""

from api.serializers.auth import CustomTokenObtainPairSerializer, UserSerializer
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that sets tokens as HTTP-only cookies."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Set HTTP-only cookies
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=settings.DEBUG is False,  # Only HTTPS in production
                samesite="Lax",
                max_age=60 * 15,  # 15 minutes
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=60 * 60 * 24 * 7,  # 7 days
            )

            # Still return user data in response body
            response.data = {"user": response.data.get("user")}

        return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout view that blacklists the refresh token and clears cookies."""
    try:
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )

        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    except Exception:
        response = Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """Get current authenticated user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view that reads refresh token from HTTP-only cookie."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Create new access token from refresh token
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response(
                {"detail": "Token refreshed successfully."}, status=status.HTTP_200_OK
            )

            # Set new access token in cookie
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=60 * 15,  # 15 minutes
            )

            return response

        except (InvalidToken, TokenError):
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
