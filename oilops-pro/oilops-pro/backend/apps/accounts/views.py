from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.services import log_action
from apps.core.permissions import IsAdminRole

from .models import User
from .serializers import ChangePasswordSerializer, EmailTokenObtainPairSerializer, UserBriefSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        email = str(request.data.get("email", "")).lower()
        user = User.objects.filter(email=email).first()
        try:
            response = super().post(request, *args, **kwargs)
        except (AuthenticationFailed, InvalidToken):
            log_action(None, "LOGIN_FAILED", "User", user.pk if user else "", email, request=request)
            raise
        log_action(user, "LOGIN", "User", user.pk if user else "", email, request=request)
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request={"application/json": {"type": "object", "properties": {"refresh": {"type": "string"}}}},
                   responses={204: None})
    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh", "")).blacklist()
        except TokenError:
            pass
        log_action(request.user, "LOGOUT", "User", request.user.pk, request.user.email, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # users may only edit their own profile basics, never role / active flag
        for field in ("role", "is_active", "email"):
            request.data.pop(field, None) if hasattr(request.data, "pop") else None
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, responses={204: None})
    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        request.user.set_password(s.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        log_action(request.user, "PASSWORD_CHANGE", "User", request.user.pk, request.user.email, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    """User administration (admins only). `directory` is open to staff for assignment pickers."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["first_name", "date_joined"]

    @extend_schema(responses=UserBriefSerializer(many=True))
    @__import__("rest_framework.decorators", fromlist=["action"]).action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated], pagination_class=None)
    def directory(self, request):
        qs = User.objects.filter(is_active=True)
        role = request.query_params.get("role")
        if role:
            qs = qs.filter(role__in=role.split(","))
        return Response(UserBriefSerializer(qs, many=True).data)
