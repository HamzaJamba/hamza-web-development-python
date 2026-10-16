from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class DeviceUser:
    """Pseudo-user for IoT gateways authenticated by X-Device-Key."""
    is_authenticated = True
    is_active = True
    is_superuser = False
    role = "DEVICE"
    pk = None
    id = None
    email = "device@oilops.local"
    full_name = "IoT device"


class DeviceKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        key = request.headers.get("X-Device-Key")
        if not key:
            return None
        if key != settings.IOT_DEVICE_API_KEY:
            raise AuthenticationFailed("Invalid device key.")
        return (DeviceUser(), None)

    def authenticate_header(self, request):
        return "X-Device-Key"
