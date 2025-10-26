"""Custom authentication classes for JWT from cookies."""

from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads the access token from cookies.

    Falls back to Authorization header if cookie is not present.
    """

    def authenticate(self, request):
        # Try to get token from cookie first
        raw_token = request.COOKIES.get("access_token")

        # Fall back to Authorization header
        if raw_token is None:
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
