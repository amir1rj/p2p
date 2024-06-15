import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager as DefaultBaseUserManager
from django.utils import timezone
from p2p import settings


class MyUserManager(DefaultBaseUserManager):

    @classmethod
    def normalize_username(cls, username):
        """
        Normalize the username by lowercasing it.
        """
        username = username or ""
        if len(username) < 4:
            raise ValueError('username must have at least 4 characters')
        return username.lower()

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def create_superuser(self, username, pin_code, PGP_key, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            username=username,
            pin_code=pin_code,
            PGP_key=PGP_key,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_user(self, username, pin_code, PGP_key, password=None, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError("The Username field must be set")

        username = self.normalize_username(username)

        user = self.model(
            username=username,
            pin_code=pin_code,
            PGP_key=PGP_key,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = models.CharField(
        verbose_name="username",
        max_length=40,
        unique=True,
    )
    is_admin = models.BooleanField(default=False, verbose_name="admin")
    pin_code = models.IntegerField(verbose_name="pin code")
    recovery_password = models.CharField(verbose_name="recovery password", max_length=255)
    balance = models.IntegerField(verbose_name="balance", default=0)
    freeze_balance = models.IntegerField(verbose_name="freeze balance", default=0)
    PGP_key = models.TextField(verbose_name="PGP key")

    objects = MyUserManager()

    REQUIRED_FIELDS = ["pin_code", 'PGP_key']
    USERNAME_FIELD = "username"

    def save(self, *args, **kwargs):
        if not self.recovery_password:
            self.recovery_password = self.generate_recovery_password()
        super().save(*args, **kwargs)

    def generate_recovery_password(self):
        unique_id = uuid.uuid4().hex
        return unique_id


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_name = models.CharField(max_length=255, verbose_name="Profile Name", unique=True)

    def __str__(self):
        return self.profile_name


class Image(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='profile_images/')

    def __str__(self):
        return f"Image for {self.profile.profile_name}"


class TempPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="tmp_passwords")
    temp_password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self) -> bool:
        """5 mins OTP validation"""

        lifespan_in_seconds = float(5 * 60)
        expiration_time = self.created_at + timezone.timedelta(seconds=lifespan_in_seconds)
        return timezone.now() <= expiration_time
