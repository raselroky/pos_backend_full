from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Q
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    use_in_migrations = True

    def _create_user(self, first_name, last_name, gender, email, phone, password, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            email=email,
            phone=phone,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_user(self, first_name, last_name, gender, email, phone, password, **extra_fields):
        print("password",password,'first_name ==',first_name)
        return self._create_user(first_name, last_name, gender, email, phone, password, False, is_active=False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(
            first_name='',
            last_name='',
            gender='male',
            email=email,
            phone='',
            password=password,
            is_superuser=True,
            is_staff=True,
            **extra_fields)
        return user

    def get_queryset(self):
        return super(CustomUserManager, self).get_queryset().filter(Q(is_active=True) | ~Q(email__regex='^#([0-9]){3}#.*'))


# When a user is deleted, its is_active field is set as False and have #ddd# as prefix. e.g. aaa@bbb.com -> #821#aaa.bbb.com
class DeletedUserManager(BaseUserManager):
    def get_queryset(self):
        return super(DeletedUserManager, self).get_queryset().filter(Q(is_active=False) & Q(email__regex='^#([0-9]){3}#.*'))

