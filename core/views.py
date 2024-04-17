from .models import *
from .serializers import *
from django.db.models import F
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

############################## Owner apis
class SignupView(APIView):
    def post(self, request):
        serializer = MyUserSerializer(data=request.data, context={'user_type': 'OWNER'})
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AddStaff(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        serializer = MyUserSerializer(data=request.data, context={'user_type': 'STAFF'})
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                'user': serializer.data,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(TokenObtainPairView):
    '''Owner/User Login API'''
    serializer_class = CustomTokenObtainPairSerializer

########### STAFF APIS
class FileFolderManager(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    queryset = FileManager.objects.all()
    serializer_class = FileManagerSerializer

    def get_queryset(self):
        user = self.request.user
        return FileManager.objects.filter(fk_user=user)
    
class FolderStructureAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, user_id, format=None):
        root_folders = FileManager.objects.filter(fk_user_id=user_id, manger_type='FOLDER', fk_folder__isnull=True)
        root_files = FileManager.objects.filter(fk_user_id=user_id, manger_type='FILE', fk_folder__isnull=True)
        
        result = self.generate_folder_structure(root_folders, root_files)
        
        return Response(result, status=status.HTTP_200_OK)
    
    def generate_folder_structure(self, folders, files):
        result = []
        
        for file in files:
            result.append({
                'type': 'FILE',
                'name': file.name,
                'url': file.file.url
            })
        
        for folder in folders:
            folder_data = {
                'type': 'FOLDER',
                'name': folder.name,
                'files-folder': []
            }
            
            child_folders = FileManager.objects.filter(fk_folder=folder, manger_type='FOLDER')
            child_files = FileManager.objects.filter(fk_folder=folder, manger_type='FILE')
            
            
            if child_folders.exists():
                folder_data['files-folder'] = self.generate_folder_structure(child_folders, [])
            
            
            for file in child_files:
                folder_data['files-folder'].append({
                    'type': 'FILE',
                    'name': file.name,
                    'url': file.file.url
                })
            
            result.append(folder_data)
        
        return result

class GetMyCompanyUsers(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    serializer_class = UserSerializer
    queryset = MyUser.objects.all()

    def get_queryset(self):
        user = self.request.user
        return MyUser.objects.filter(company=user.company).exclude(pk=user.id)
    
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            access_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)