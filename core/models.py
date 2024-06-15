from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models


class BaseManager(models.Manager):
    """
    The base manager class
    """

    def get_queryset(self):
        """
        Won't show objects while is_delete is True
        """
        return super().get_queryset().filter(is_delete=False)

    def get_all(self):
        """
        Will get all objects
        """
        return super().get_queryset()


class BaseModel(models.Model):
    """
    The BaseModel class for interacting
    """
    objects = BaseManager()
    create_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    modify_datetime = models.DateTimeField(auto_now=True, editable=False)
    is_active = models.BooleanField(default=True, editable=False)
    is_delete = models.BooleanField(default=False, editable=False)

    class Meta:
        """
        Won't save on database
        """
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Instead of completely deleting it will only set is_delete True
        :param keep_parents: Will not keep parents upon deletion
        :param using:
        """
        self.is_delete = True
        self.save()

    def undelete(self):
        """
        Restoring deleted data by setting is_delete False
        :return:
        """
        self.is_delete = False
        self.save()

    def active(self):
        """
        Setting is_active True to activating the data
        :return:
        """
        self.is_active = True
        self.save()

    def deactivate(self):
        """
        Setting is_active False to deactivating the data
        :return:
        """
        self.is_active = False
        self.save()


class BaseUserManager(models.Manager):

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

    def create_superuser(self, username, pin_code, PGP_key, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            PGP_key=PGP_key,
            password=password,
            username=username,
            pin_code=pin_code
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def create_user(self, username, pin_code, PGP_key, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError("Users must have an phone number")

        user = self.model(

            PGP_key=PGP_key,
            password=password,
            username=username,
            pin_code=pin_code
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
