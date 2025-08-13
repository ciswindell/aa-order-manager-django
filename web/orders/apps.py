from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self) -> None:  # pragma: no cover
        # Import signal handlers
        from . import signals  # noqa: F401

        return None
