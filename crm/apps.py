# crm/apps.py

from django.apps import AppConfig


class CrmConfig(AppConfig):
    """
    Configuration class for the CRM application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "crm"
    verbose_name = "Customer Relationship Management"
