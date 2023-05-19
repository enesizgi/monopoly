from django.apps import AppConfig


class MonopolyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monopoly'

    def ready(self):
        print('Monopoly app is ready!')
        import monopoly.signals
