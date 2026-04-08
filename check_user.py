import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    u = User.objects.get(username="kuku")
    print("Username:", u.username)
    print("Role:", getattr(u, 'role', 'NO_ROLE_FIELD'))
    print("Is active:", u.is_active)
    print("Password check (kuku123):", u.check_password("kuku123"))
except User.DoesNotExist:
    print("User kuku does not exist.")
