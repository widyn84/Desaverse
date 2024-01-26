from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.password_validation import validate_password
import json

from myapp.models import *

class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        return getattr(self._choices, data)
    
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(raw_password=validated_data['password'])
        user.save()

        token = get_random_string(length=50)
        Account.objects.create(user=user, verification_token=token, type_account="PUBLIC")

        verification_url = f"https://dev.desaverse.co.id/verification/{token}"
        context = {'user':user, 'verification_url':verification_url}
        html_message = render_to_string('verification_email.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            'Verify Your Email',
            plain_message,
            'from@desaverse.com',
            [user.email],
            html_message=html_message
        )
        return user

class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=50)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }

class UserUpdateAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ManagerChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerChannel
        fields = ('channel', 'start_managing', 'end_managing')

class ChannelManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerChannel
        fields = ('account_manager', 'start_managing', 'end_managing')

class CreateManagerChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerChannel
        fields = ('account_manager', 'start_managing', 'end_managing')

class DeleteManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerChannel
        fields = '__all__'

class GetAccountSerializer(serializers.ModelSerializer):
    user = GetUserSerializer(required=False, read_only=True, allow_null=True)
    type_account = serializers.CharField(source='get_type_account_display')
    foto_account = serializers.SerializerMethodField()
    manager = ManagerChannelSerializer(required=False, read_only=True, allow_null=True)
    class Meta:
        model = Account
        fields = ('id', 'user', 'foto_account', 'type_account', 'deskripsi_account', 'no_telpon','manager')
    
    def get_foto_account(self, obj):
        foto_url = obj.foto_account.url
        return f'https://api.desaverse.co.id{foto_url}'

class UpdateAccountSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(partial=True, required=False)
    class Meta:
        model = Account
        fields = ('user', 'foto_account', 'deskripsi_account', 'no_telpon')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

        return super().update(instance, validated_data)

class UpdateAccounAdminSerializer(serializers.ModelSerializer):
    user = UserUpdateAdminSerializer()
    class Meta:
        model = Account
        fields = ('user', 'foto_account', 'type_account', 'deskripsi_account', 'no_telpon', 'email_verified')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_instance = instance.user
            user_serializer = UserUpdateAdminSerializer(user_instance, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    
class ChangePassworAdminSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    
class CreateChannelSerializer(serializers.ModelSerializer):
    account = GetAccountSerializer(required=False, read_only=True, allow_null=True)

    class Meta:
        model = Channel
        fields = ('account', 'nama_channel', 'akronim', 'deskripsi', 'logo', 'daerah', 'alamat')


class ListChannelSerializer(serializers.ModelSerializer):
    account = GetAccountSerializer(required=False, read_only=True, allow_null=True)
    logo = serializers.SerializerMethodField()
    channel_managed = ChannelManagerSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Channel
        fields = ('id', 'account', 'nama_channel', 'akronim', 'deskripsi', 'logo', 'isActive', 'isModerated', 'daerah', 'alamat', 'channel_managed')
    
    def get_logo(self, obj):
        if obj.logo:
            logo_url = obj.logo.url
            return f'https://api.desaverse.co.id{logo_url}'
        return None

class GetDetailChannelSerializer(serializers.ModelSerializer):
    account = GetAccountSerializer(required=False, read_only=True, allow_null=True)
    channel_managed = ChannelManagerSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = Channel
        fields = '__all__'

class GetChannelRetrieveSerializer(serializers.ModelSerializer):
    account = GetAccountSerializer(required=False, read_only=True, allow_null=True)
    channel_managed = ChannelManagerSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = Channel
        fields = '__all__'

class UpdateChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('nama_channel', 'akronim', 'deskripsi', 'logo', 'daerah', 'alamat')

class DeleteChannelSerializer(serializers.ModelSerializer):
    account = GetAccountSerializer(required=False, read_only=True, allow_null=True)
    class Meta:
        model = Channel
        fields = '__all__'

class CreateVerificationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelVerification
        fields = ('channel', 'foto_ktp', 'surat_keterangan')

class UpdateStatusVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelVerification
        fields = ('status_verifikasi', 'pesan')

class ListVerificationChannelSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer()
    class Meta:
        model = ChannelVerification
        fields = ('id', 'channel', 'foto_ktp', 'surat_keterangan', 'status_verifikasi', 'pesan', 'created', 'updated')

class DeleteVerificationChannelSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer()
    class Meta:
        model = ChannelVerification
        fields = ('id', 'channel', 'foto_ktp', 'surat_keterangan', 'status_verifikasi', 'pesan', 'created', 'updated')

class CreatorContentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Account
        fields = ('username', )

class UpdatedContentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Account
        fields = ('username', )

class LikedBy(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Account
        fields = ('id', 'username')

class GetListVideoSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer(required=False, read_only=True)
    creator = CreatorContentSerializer(read_only=True)
    updated_by = UpdatedContentSerializer(read_only=True)
    liked_by = LikedBy(many=True, read_only=True)
    
    class Meta:
        model = ContentVideo
        fields = '__all__'

class GetVideoRetrieveSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer()
    file_video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    creator = CreatorContentSerializer(read_only=True)
    updated_by = UpdatedContentSerializer(read_only=True)
    liked_by = LikedBy(many=True, read_only=True)

    class Meta:
        model = ContentVideo
        fields = '__all__'
    
    def get_file_video(self, obj):
        if obj.file_video:
            file_video_url = obj.file_video.url
            return f'https://api.desaverse.co.id{file_video_url}'
        return None
    
    def get_thumbnail(self, obj):
        if obj.thumbnail:
            thumbnail = obj.thumbnail.url
            return f'https://api.desaverse.co.id{thumbnail}'
        return None

class CreateVideoSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ContentVideo
        fields = ('judul_video', 'kategori_video', 'file_video', 'thumbnail', 'deskripsi')

class UpdateVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVideo
        fields = ('judul_video', 'kategori_video', 'thumbnail', 'deskripsi')

class DeleteVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVideo
        fields = '__all__'

class CreateGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('kategori_galeri', 'foto', 'deskripsi')

class GetListGallerySerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer(required=False, read_only=True)
    creator = CreatorContentSerializer(read_only=True)
    updated_by = UpdatedContentSerializer(read_only=True)
    liked_by = LikedBy(many=True, read_only=True)  
    class Meta:
        model = Gallery
        fields = '__all__'

class GetGalleryRetrieveSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer()
    foto = serializers.SerializerMethodField()
    creator = CreatorContentSerializer(read_only=True)
    updated_by = UpdatedContentSerializer(read_only=True)
    liked_by = LikedBy(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = '__all__'
    
    def get_foto(self, obj):
        if obj.foto:
            foto_url = obj.foto.url
            return f'https://api.desaverse.co.id{foto_url}'
        return None

class UpdateGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('kategori_galeri', 'deskripsi')

class DeleteGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class CreateArticleSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('kategori_artikel', 'judul_artikel', 'cover_artikel', 'konten_artikel')

class GetListArticleSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer(required=False, read_only=True)
    creator = CreatorContentSerializer(read_only=True)
    updated_by = UpdatedContentSerializer(read_only=True)
    liked_by = LikedBy(many=True, read_only=True)
    class Meta:
        model = Article
        fields = '__all__'

class GetArticleRetrieveSerializer(serializers.ModelSerializer):
    channel = ListChannelSerializer()
    cover_artikel = serializers.SerializerMethodField()
    creator = CreatorContentSerializer(read_only=True)
    updated_by = UpdatedContentSerializer(read_only=True)
    liked_by = LikedBy(many=True, read_only=True)
    class Meta:
        model = Article
        fields = '__all__'
    
    def get_cover_artikel(self, obj):
        if obj.cover_artikel:
            cover_artikel_url = obj.cover_artikel.url
            return f'https://api.desaverse.co.id{cover_artikel_url}'
        return None

class UpddateArticleSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('kategori_artikel', 'judul_artikel', 'cover_artikel', 'konten_artikel')

class DeleteArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ReviewVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVideo
        fields = ('status', 'pesan_status')

class ReviewGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ('status', 'pesan_status')

class ReviewArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('status', 'pesan_status')

class LikeVideoSerializer(serializers.ModelSerializer):
    video = GetVideoRetrieveSerializer()
    class Meta:
        model = LikeVideo
        fields = '__all__'

class LikeGallerySerializer(serializers.ModelSerializer):
    gallery = GetGalleryRetrieveSerializer()
    class Meta:
        model = LikeGallery
        fields = '__all__'

class LikeArticleSerializer(serializers.ModelSerializer):
    article = GetArticleRetrieveSerializer()
    class Meta:
        model = LikeArticle
        fields = '__all__'
