import os, traceback
from django.db import models
from .managers import MyUserManager
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

##### SIGNAL TO DELETE THE FILE FROM STORAGE 
def delete_file(sender, instance, **kwargs):
	try:
		os.remove(os.path.join(instance.file.path))
	except:
		traceback.print_exc()
            
class Company(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)

class MyUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE = [
        ('OWNER', 'OWNER'),
        ('STAFF', 'STAFF'),
    ]

    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE, default='STAFF')
    is_staff = models.BooleanField(default=False)
    fk_owner = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='self_user')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return self.username
    
class FileManager(models.Model):
    MANGER_TYPE = [
        ('FILE', 'FILE'),
        ('FOLDER', 'FOLDER'),
    ]

    fk_user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    manger_type = models.CharField(max_length=10, choices=MANGER_TYPE)
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='Files/', blank=True, null=True)
    fk_folder = models.ForeignKey('self',  on_delete=models.CASCADE, null=True, blank=True, related_name='self_folder')
    created_at = models.DateTimeField(auto_now=True)

# register signal for deleting file 
post_delete.connect(delete_file, sender=FileManager)