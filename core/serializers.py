from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'company', 'user_type']

class MyUserSerializer(serializers.ModelSerializer):
    company = serializers.CharField(write_only=True, required=False)
    owner = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = MyUser
        fields = ['company', 'username', 'password', 'owner']

    def create(self, validated_data):
        user = None
        user_type = self.context.get('user_type')
        if user_type == 'STAFF':
            if not 'owner' in validated_data:
                raise serializers.ValidationError('Owner for staff is required.')
            else:
                owner = validated_data.pop('owner')
                owner = MyUser.objects.filter(username=owner).last()
                if owner:
                    user = MyUser.objects.create(fk_owner=owner, company=owner.company, **validated_data)
                    user.set_password(validated_data['password'])
                    user.save()
                else:
                    raise serializers.ValidationError('Sorry !!! we unable to find the owner in our system, please check the username and try again.')
        else:
            company_data = validated_data.pop('company')
            company = Company.objects.filter(name=company_data).last()
            if company:
                raise serializers.ValidationError("This company has already been registered with another owner.")

            company = Company.objects.create(name=company_data)
            user = MyUser.objects.create(company=company, user_type=user_type, **validated_data)
            user.set_password(validated_data['password'])
            user.save()

        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
    
class FileManagerSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=True, write_only=True)
    user_id = serializers.IntegerField(required=True, write_only=True)
    folder_id = serializers.IntegerField(required=False, write_only=True)
    
    fk_user = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    manger_type = serializers.ChoiceField(choices=FileManager.MANGER_TYPE, required=False, read_only=True)

    class Meta:
        model = FileManager
        fields = ['user_id', 'name', 'type', 'file', 'folder_id', 'fk_user', 'created_at', 'manger_type']

    def validate(self, data):
        user_id = data.get('user_id')
        folder_id = data.get('folder_id')
        if user_id:
            try:
                MyUser.objects.get(pk=user_id, user_type='STAFF')
            except:
                raise serializers.ValidationError('User with provided ID does not exist.')

        if folder_id:
            try:
                FileManager.objects.get(pk=folder_id, manger_type='FOLDER')
            except:
                raise serializers.ValidationError('Folder with provided ID does not exist.')

        type = data.get('type')
        if type == 'FILE' and not data.get('file'):
            raise serializers.ValidationError("file is required for file creation")

        if FileManager.objects.filter(fk_user_id=user_id, name=data['name'], fk_folder_id=folder_id).exists():
            raise serializers.ValidationError("We found the entry with same name in the records.")
            
        return data

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        folder_id = validated_data.pop('folder_id', None)
        manger_type = validated_data.pop('type')

        file_manager = FileManager.objects.create(**validated_data, fk_user_id=user_id, fk_folder_id=folder_id, manger_type=manger_type)
        return file_manager