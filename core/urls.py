from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'filemanager', FileFolderManager) 
router.register(r'company-users', GetMyCompanyUsers) 

urlpatterns = [
    path('', include(router.urls)),

    path('register/', SignupView.as_view(), name='user_registration'),
    path('add-staff/', AddStaff.as_view(), name='add_staff_by_owner'),
    path('login/', LoginView.as_view(), name='owner_user_login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('folder-structure/<int:user_id>/', FolderStructureAPIView.as_view(), name='folder-structure'),
]