from django.apps import AppConfig

class UserinfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.userinfo'

    def ready(self):
        import apps.userinfo.signals

