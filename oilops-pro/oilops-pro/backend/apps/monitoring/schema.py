from drf_spectacular.extensions import OpenApiAuthenticationExtension


class DeviceKeyScheme(OpenApiAuthenticationExtension):
    target_class = "apps.monitoring.auth.DeviceKeyAuthentication"
    name = "DeviceKey"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "header", "name": "X-Device-Key",
                "description": "Shared key for IoT gateways posting telemetry."}
