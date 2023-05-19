from datetime import timezone

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

users = []

@receiver(user_logged_in)
def user_logged_in_receiver(sender, request, user, **kwargs):
    # Perform your extra actions here
    # For example, you can log the login activity, update user's last login timestamp, etc.
    # You can access the logged-in user using the 'user' argument

    # Example: Log the login activity
    print(f"User {user.username} logged ")
    users.append(user.username)
    print(users)
