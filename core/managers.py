
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
	def _create_user(self, username, password, company, user_type, fk_owner, is_staff, is_superuser, **extra_fields):
		if not username:
			raise ValueError('Users must have username...')

		now = timezone.now()

		username = username
		user = self.model(
			username = username, 
			company = company,
			user_type = user_type,
			is_staff=is_staff,
			is_superuser=is_superuser, 
			last_login=now,
			fk_owner = fk_owner,
			**extra_fields
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, password, **extra_fields):
		return self._create_user(username, password, False, False, **extra_fields)

	def create_superuser(self, username, password, **extra_fields):
		user=self._create_user(username, password, None, '', None, True, True, **extra_fields)
		return user
	
