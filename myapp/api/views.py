from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from .permissions import IsOwnerOrManagerOrReadOnly
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from myapp.models import *
from .serializers import *
from datetime import datetime
from django.http import Http404
from django.db.models import Count
from django.db import transaction
from django.db.models import Q
import os
import shutil

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data['username'])
            account = Account.objects.get(user=user)
            if not account.email_verified:
                return Response({'Error': "Email Belum Diverifikasi"}, status=status.HTTP_400_BAD_REQUEST)
        return response

class CreateUserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]

    def perform_create(self, serializer):
        serializer.save()

class VerifyEmailViewSet(viewsets.ModelViewSet):
    serializer_class = VerifyEmailSerializer

    def create(self, request, *args, **kwargs):
       serializer = self.get_serializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       token = serializer.validated_data['token']

       try:
           account = Account.objects.get(verification_token=token)
       except Account.DoesNotExist:
           return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
       
       account.email_verified = True
       account.verification_token = None
       account.save()
       return Response({'message': 'Verifikasi Email Berhasil!'})
    
class ListAccountView(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = GetAccountSerializer
    permission_classes = [HasAPIKey]

class GetAccountRetrieveView(viewsets.ModelViewSet):
    serializer_class = GetAccountSerializer
    queryset = Account.objects.all()
    permission_classes = [HasAPIKey]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'Akun tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

class GetDetailAccountView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request):
        user = request.user
        account = Account.objects.get(user = user)
        serializer = GetAccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateAccountView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UpdateAccountSerializer
    queryset = Account.objects.all()

    def get_object(self):
        return Account.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        user_data = self.request.data.get('user', {})
        UserSerializer(self.request.user, data=user_data, partial=True).is_valid(raise_exception=True)
        serializer.save()

class UpdateAccountAdminView(viewsets.ModelViewSet):
    permission_class = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UpdateAccounAdminSerializer
    queryset = Account.objects.all()

    def partial_update(self, request, *args, **kwargs):
        if not request.user.account.type_account == 'ADMIN':
            return Response({'detail': 'Anda tidak diizinkan untuk melakukan tindakan ini!'}, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangePasswordViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')
            
            if not user.check_password(old_password):
                return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            return Response({'success': 'Password has been changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordAdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, pk=None):
        if not request.user.account.type_account == 'ADMIN':
            return Response({'error': 'Only Superadmin can perform this action'}, status=status.HTTP_403_FORBIDDEN)

        account_id = pk
        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChangePassworAdminSerializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')

            # Set password baru untuk akun yang bersangkutan
            account.user.set_password(new_password)
            account.user.save()

            return Response({'success': 'Password has been changed successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
class UserDeleteView(viewsets.ModelViewSet):
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            account = Account.objects.get(user=user)
            folder_path = os.path.dirname(account.get_upload_path(""))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            account.delete()
        except Account.DoesNotExist:
            pass

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UserDeleteAdminViewSet(viewsets.ModelViewSet):
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if not self.request.user.account.type_account == 'ADMIN':
            return Account.objects.none()
        return Account.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        try:
            account = self.get_object()
            user = account.user
            account.delete()
            upload_path = account.get_upload_path("")
            shutil.rmtree(upload_path, ignore_errors=True)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

class CreateChannelView(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = CreateChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        existing_channel = Channel.objects.filter(account=request.user.account).first()
        if existing_channel:
            return Response(
                {'detail': 'Akun ini sudah memiliki channel'},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(account=request.user.account)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class CreateVerificationChannelView(viewsets.ModelViewSet):
    queryset = ChannelVerification.objects.all()
    serializer_class = CreateVerificationChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        existing_verification = ChannelVerification.objects.filter(
            channel__account__user=request.user,
            status_verifikasi__in=['pending']
        ).first()

        if existing_verification:
            return Response(
                {"message": "Anda sudah memiliki permintaan verifikasi yang sedang diproses"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_account = request.user.account  # Get the user's account
        if user_account:
            channel = user_account.owner  # Get the first channel associated with the account
            if channel:
                request.data['channel'] = channel.id
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(
            {"message": "Akun Anda tidak terkait dengan channel"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        serializer.save()
 
class UpdateStatusVerificationView(viewsets.ModelViewSet):
    queryset = ChannelVerification.objects.all()
    serializer_class = UpdateStatusVerificationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Jika Bukan Verifikator
        if request.user.account.type_account != 'VERIFIKATOR':
            return Response({"detail": "Anda Tidak Memiliki Akses Untuk Melakukan Update Ini"}, status=status.HTTP_403_FORBIDDEN)
        
        # Jika Status Tidak Pending
        if instance.status_verifikasi != 'pending':
            return Response({"detail": "Status Verifikasi Tidak Bisa Diubah"}, status=status.HTTP_400_BAD_REQUEST)
        
        instance.status_verifikasi = request.data.get('status_verifikasi', instance.status_verifikasi)
        instance.pesan = request.data.get('pesan', instance.pesan)
        instance.save()

        if instance.status_verifikasi == 'verified':
            instance.channel.isModerated = True
            instance.channel.save()

            instance.channel.account.type_account = 'CHANNEL'
            instance.channel.account.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class GetListVerificationAdminView(viewsets.ModelViewSet):
    serializer_class = ListVerificationChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if self.request.user.account.type_account == 'VERIFIKATOR':
            return ChannelVerification.objects.all()
        else:
            return Response({"detail": "Anda Tidak Memiliki Akses"}, status=status.HTTP_403_FORBIDDEN)

class GetListVerificationAdminRetrieveView(viewsets.ModelViewSet):
    serializer_class = ListVerificationChannelSerializer
    queryset = ChannelVerification.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def retrieve(self, request, *args, **kwargs):
                    # Jika Bukan Verifikator
        if request.user.account.type_account != 'VERIFIKATOR':
            return Response({"detail": "Anda Tidak Memiliki Akses Untuk Melihat Daata Ini!"}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'Data verifikasi tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)


class GetListVerificationUserView(viewsets.ModelViewSet):
    serializer_class = ListVerificationChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return ChannelVerification.objects.filter(channel__account__user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeleteVerificationUserView(viewsets.ModelViewSet):
    serializer_class = DeleteVerificationChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return ChannelVerification.objects.filter(channel__account__user=self.request.user)
    
    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.get(pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status_verifikasi in ['verified', 'rejected']:
            return  Response(
                {"message": "Anda tidak dapat menghapus hasil verifikasi yang sudah diverifikasi atau ditolak"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if instance.foto_ktp:
            file_path = instance.foto_ktp.path
            if os.path.exists(file_path):
                os.remove(file_path)

        if instance.surat_keterangan:
            file_path = instance.surat_keterangan.path
            if os.path.exists(file_path):
                os.remove(file_path)

        self.perform_destroy(instance)
        return Response(
            {"message": "Berhasil menghapus pengajuan verifikasi"},
            status=status.HTTP_204_NO_CONTENT
        )

class ListChannelView(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ListChannelSerializer
    permission_classes = [HasAPIKey]

class GetDetailChannelView(viewsets.ModelViewSet):
    serializer_class = GetDetailChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request):
        user = request.user
        try:
            account = Account.objects.get(user = user)
            channel_queryset = Channel.objects.filter(
                Q(account=account) | Q(channel_managed__account_manager=account)
            ).distinct()

            channel = channel_queryset.first()

            if not channel:
                return Response({'detail': 'Akun ini tidak memiliki channel'}, status=status.HTTP_200_OK)

        except (Account.DoesNotExist):
            return Response({'detail': 'Akun ini tidak terkait dengan channel'}, status = status.HTTP_200_OK)
        except (Channel.DoesNotExist):
            return Response({'detail': 'Channel tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(channel)
        return Response(serializer.data)

class GetChannelRetrieveView(viewsets.ModelViewSet):
    serializer_class = GetChannelRetrieveSerializer
    queryset = Channel.objects.all()
    permission_classes = [HasAPIKey]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'Channel tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

class UpdateChannelView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UpdateChannelSerializer
    queryset = Channel.objects.all()

    def get_object(self):
        account = self.request.user.account
        return Channel.objects.get(account=account)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
class DeleteChannelView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = DeleteChannelSerializer
    queryset = Channel.objects.all()

    def get_object(self):
        account = self.request.user.account
        return Channel.objects.get(account=account)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        channel_id = instance.id

        channel_folder_path = f"assets/channel-{channel_id}"
        shutil.rmtree(channel_folder_path, ignore_errors=True)

        if instance.account.type_account == 'CHANNEL':
            instance.account.type_account = 'PUBLIC'
            instance.account.save()

        channel_managers = ManagerChannel.objects.filter(channel_id=channel_id)
        for manager in channel_managers:
            manager_account = manager.account_manager
            manager_account.type_account = 'PUBLIC'
            manager_account.save()
        

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateManagerChannelView(viewsets.ModelViewSet):
    queryset = ManagerChannel.objects.all()
    serializer_class = CreateManagerChannelSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account_manager = serializer.validated_data['account_manager']

        if ManagerChannel.objects.filter(account_manager=account_manager).exists():
            return Response({'detail': 'Akun ini sudah menjadi pengelola di channel lain'}, status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(account_manager, 'owner'):
            return Response({'detail': 'Akun ini sudah memiliki channel tidak bisa menjadi manager'}, status=status.HTTP_400_BAD_REQUEST)
        
        channel = Channel.objects.get(account=request.user.account)

        account_manager.type_account = "CHANNEL MANAGER"
        account_manager.save()

        serializer.validated_data['channel'] = channel
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class DeleteManagerChannelView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = DeleteManagerSerializer
    queryset = ManagerChannel.objects.all()
   
    def get_object(self):
        account_id = self.kwargs['account_id']
        return get_object_or_404(self.queryset, account_manager__id=account_id)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.channel.account != request.user.account:
            return Response({'detail': 'Anda tidak memiliki izin untuk menghapus pengelola  dari channel ini'}, status=status.HTTP_403_FORBIDDEN)

        account_manager = instance.account_manager
        instance.delete()
        account_manager.type_account = 'PUBLIC'
        account_manager.save()
        return Response({'detail': 'Pengelola Channel berhasil dihapus!'}, status=status.HTTP_204_NO_CONTENT)

class GetListVideoChannelView(viewsets.ReadOnlyModelViewSet):
    serializer_class = GetListVideoSerializer
    permission_classes = [HasAPIKey]
    
    def get_queryset(self):
        channel_id = self.kwargs.get('pk')
        channel = get_object_or_404(Channel, id=channel_id)
        return ContentVideo.objects.filter(channel=channel)

class GetListVideosView(viewsets.ModelViewSet):
    serializer_class = GetListVideoSerializer
    permission_classes = [HasAPIKey]
    queryset = ContentVideo.objects.all()

class GetVideoRetrieveView(viewsets.ViewSet):
    serializer_class = GetVideoRetrieveSerializer
    permission_classes = [HasAPIKey]

    def retrieve(self, request, channel_pk=None, video_pk=None, *args, **kwargs):
        channel = get_object_or_404(Channel, pk=channel_pk)
        video = get_object_or_404(ContentVideo, pk=video_pk, channel=channel)
        serializer = self.serializer_class(video)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateVideoView(viewsets.ModelViewSet):
    queryset = ContentVideo.objects.all()
    serializer_class = CreateVideoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        account = request.user.account
        try:
            manager_channel = ManagerChannel.objects.get(account_manager = account)
            channel = manager_channel.channel
            creator = account
        except:
            channel = Channel.objects.get(account=account)
            creator = account

        if not channel.isModerated:
            return Response({'error': 'Channel harus dimoderasi sebelum membuat video.'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.data['status'] = 'pending'

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['channel'] = channel
            serializer.validated_data['creator'] = creator
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateVideoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrReadOnly ]
    authentication_classes = [TokenAuthentication]
    serializer_class = UpdateVideoSerializer
    queryset = ContentVideo.objects.all()

    def get_object(self):
        video_pk = self.kwargs['video_pk']
        video = get_object_or_404(ContentVideo, pk=video_pk)
        return video
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if (instance.channel.account == request.user.account) or (instance.channel.channel_managed.filter(account_manager=request.user.account).exists()):
            instance.updated_by = request.user.account
            instance.save()

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user.account)

            return Response(serializer.data)
        else:
            return Response({'detail': 'Anda tidak memiliki izin untuk update video dari channel ini'}, status=status.HTTP_403_FORBIDDEN)
    
class DeleteVideoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    serializer_class = DeleteVideoSerializer
    queryset = ContentVideo.objects.all()

    def get_object(self):
        video_pk = self.kwargs['video_pk']
        video = get_object_or_404(ContentVideo, pk=video_pk)
        return video
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        is_owner_or_manager = (
            instance.channel.account == request.user.account or
            instance.channel.channel_managed.filter(account_manager=request.user.account).exists()
        )

        if not is_owner_or_manager:
            return Response({'detail': 'Anda tidak memiliki izin untuk menghapus video dari channel ini'}, status=status.HTTP_403_FORBIDDEN)
        

        video_file_path = instance.file_video.path
        if os.path.exists(video_file_path):
            os.remove(video_file_path)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateGalleryView(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = CreateGallerySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        account = request.user.account
        try:
            manager_channel = ManagerChannel.objects.get(account_manager = account)
            channel = manager_channel.channel
            creator = account
        except:
            channel = Channel.objects.get(account=account)
            creator = account

        if not channel.isModerated:
            return Response({'error': 'Channel harus dimoderasi sebelum membuat galeri.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['channel'] = channel
            serializer.validated_data['creator'] = creator
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetListGalleryChannelView(viewsets.ReadOnlyModelViewSet):
    serializer_class = GetListGallerySerializer
    permission_classes = [HasAPIKey]
    
    def get_queryset(self):
        channel_id = self.kwargs.get('pk')
        channel = get_object_or_404(Channel, id=channel_id)
        return Gallery.objects.filter(channel=channel)

class GetListGalleriesView(viewsets.ModelViewSet):
    serializer_class = GetListGallerySerializer
    permission_classes = [HasAPIKey]
    queryset = Gallery.objects.all()

class GetGalleryRetrieveView(viewsets.ViewSet):
    serializer_class = GetGalleryRetrieveSerializer
    permission_classes = [HasAPIKey]

    def retrieve(self, request, channel_pk=None, gallery_pk=None, *args, **kwargs):
        channel = get_object_or_404(Channel, pk=channel_pk)
        gallery = get_object_or_404(Gallery, pk=gallery_pk, channel=channel)
        serializer = self.serializer_class(gallery)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateGalleryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrReadOnly ]
    authentication_classes = [TokenAuthentication]
    serializer_class = UpdateGallerySerializer
    queryset = Gallery.objects.all()

    def get_object(self):
        gallery_pk = self.kwargs['gallery_pk']
        gallery = get_object_or_404(Gallery, pk=gallery_pk)
        return gallery
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if (instance.channel.account == request.user.account) or (instance.channel.channel_managed.filter(account_manager=request.user.account).exists()):
            instance.updated_by = request.user.account
            instance.save()

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user.account)

            return Response(serializer.data)
        else:
            return Response({'detail': 'Anda tidak memiliki izin untuk update galeri dari channel ini'}, status=status.HTTP_403_FORBIDDEN)

class DeleteGalleryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    serializer_class = DeleteGallerySerializer
    queryset = Gallery.objects.all()

    def get_object(self):
        gallery_pk = self.kwargs['gallery_pk']
        gallery = get_object_or_404(Gallery, pk=gallery_pk)
        return gallery
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        is_owner_or_manager = (
            instance.channel.account == request.user.account or
            instance.channel.channel_managed.filter(account_manager=request.user.account).exists()
        )

        if not is_owner_or_manager:
            return Response({'detail': 'Anda tidak memiliki izin untuk menghapus galeri dari channel ini'}, status=status.HTTP_403_FORBIDDEN)

        gallery_file_path = instance.foto.path
        if os.path.exists(gallery_file_path):
            os.remove(gallery_file_path)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateArticleView(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = CreateArticleSerialzier
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def create(self, request, *args, **kwargs):
        account = request.user.account
        try:
            manager_channel = ManagerChannel.objects.get(account_manager = account)
            channel = manager_channel.channel
            creator = account
        except:
            channel = Channel.objects.get(account=account)
            creator = account

        if not channel.isModerated:
            return Response({'error': 'Channel harus dimoderasi sebelum membuat artikel.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['channel'] = channel
            serializer.validated_data['creator'] = creator
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetListArticlesView(viewsets.ModelViewSet):
    serializer_class = GetListArticleSerializer
    permission_classes = [HasAPIKey]
    queryset = Article.objects.all()

class GetListArticleChannelView(viewsets.ModelViewSet):
    serializer_class = GetListArticleSerializer
    permission_classes = [HasAPIKey]
    
    def get_queryset(self):
        channel_id = self.kwargs.get('pk')
        channel = get_object_or_404(Channel, id=channel_id)
        return Article.objects.filter(channel=channel)

class GetArticleRetrieveView(viewsets.ViewSet):
    serializer_class = GetArticleRetrieveSerializer
    permission_classes = [HasAPIKey]

    def retrieve(self, request, channel_pk=None, article_pk=None, *args, **kwargs):
        channel = get_object_or_404(Channel, pk=channel_pk)
        article = get_object_or_404(Article, pk=article_pk, channel=channel)
        serializer = self.serializer_class(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateArticleView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrReadOnly ]
    authentication_classes = [TokenAuthentication]
    serializer_class = UpddateArticleSerialzier
    queryset = Article.objects.all()

    def get_object(self):
        article_pk = self.kwargs['article_pk']
        article = get_object_or_404(Article, pk=article_pk)
        return article
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if (instance.channel.account == request.user.account) or (instance.channel.channel_managed.filter(account_manager=request.user.account).exists()):
            instance.updated_by = request.user.account
            instance.save()

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user.account)

            return Response(serializer.data)
        else:
            return Response({'detail': 'Anda tidak memiliki izin untuk update artikel dari channel ini'}, status=status.HTTP_403_FORBIDDEN)

class DeleteArticleView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrManagerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    serializer_class = DeleteArticleSerializer
    queryset = Article.objects.all()

    def get_object(self):
        article_pk = self.kwargs['article_pk']
        article = get_object_or_404(Article, pk=article_pk)
        return article
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        is_owner_or_manager = (
            instance.channel.account == request.user.account or
            instance.channel.channel_managed.filter(account_manager=request.user.account).exists()
        )

        if not is_owner_or_manager:
            return Response({'detail': 'Anda tidak memiliki izin untuk menghapus artikel dari channel ini'}, status=status.HTTP_403_FORBIDDEN)

        article_file_path = instance.cover_artikel.path
        if os.path.exists(article_file_path):
            os.remove(article_file_path)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewVideoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ReviewVideoSerializer
    queryset = ContentVideo.objects.all()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.account.type_account != 'REVIEWER':
            return Response({'detail': 'Anda tidak memiliki izin untuk melakukan tindakan ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if instance.status != 'pending':
            return Response({'error': 'Hanya status pending yang dapat diubah'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        if instance.status == 'accepted':
            instance.channel.isActive = True
            instance.channel.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReviewGalleryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ReviewGallerySerializer
    queryset = Gallery.objects.all()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.account.type_account != 'REVIEWER':
            return Response({'detail': 'Anda tidak memiliki izin untuk melakukan tindakan ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if instance.status != 'pending':
            return Response({'error': 'Hanya status pending yang dapat diubah'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if instance.status == 'accepted':
            instance.channel.isActive = True
            instance.channel.save()        
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReviewArticleView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ReviewArticleSerializer
    queryset = Article.objects.all()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.account.type_account != 'REVIEWER':
            return Response({'detail': 'Anda tidak memiliki izin untuk melakukan tindakan ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if instance.status != 'pending':
            return Response({'error': 'Hanya status pending yang dapat diubah'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if instance.status == 'accepted':
            instance.channel.isActive = True
            instance.channel.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class LikeVideoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeVideo.objects.all()
    serializer_class = LikeVideoSerializer

    def create(self, request, video_pk, *args, **kwargs):
        account = request.user.account

        video = ContentVideo.objects.get(pk=video_pk)

        try:
            like_instance = LikeVideo.objects.get(account=account, video=video)
            return Response({'detail': 'Anda sudah malakukan like pada video ini'}, status=status.HTTP_400_BAD_REQUEST)
        except LikeVideo.DoesNotExist:
            LikeVideo.objects.create(account=account, video=video)
            return Response({'detail': 'Video berhasil dilike!'}, status=status.HTTP_201_CREATED)

class UnlikeVideoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeVideo.objects.all()
    serializer_class = LikeVideoSerializer

    def destroy(self, request, video_pk, *args, **kwargs):
        account = request.user.account
        video = get_object_or_404(ContentVideo, pk=video_pk)

        try:
            like_instance = LikeVideo.objects.get(account=account, video=video)
            like_instance.delete()

            return Response({'detail': 'Video berhasil diunlike'}, status=status.HTTP_200_OK)
        except LikeVideo.DoesNotExist:
            return Response({'detail': 'Anda belum melakukan like pada video ini'}, status=status.HTTP_400_BAD_REQUEST)
        except ContentVideo.DoesNotExist:
            return Response({'detail': 'Video tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

class LikeGalleryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeGallery.objects.all()
    serializer_class = LikeGallerySerializer

    def create(self, request, gallery_pk, *args, **kwargs):
        account = request.user.account

        gallery = Gallery.objects.get(pk=gallery_pk)

        try:
            like_instance = LikeGallery.objects.get(account=account, gallery=gallery)
            return Response({'detail': 'Anda sudah malakukan like pada gallery ini'}, status=status.HTTP_400_BAD_REQUEST)
        except LikeGallery.DoesNotExist:
            LikeGallery.objects.create(account=account, gallery=gallery)
            return Response({'detail': 'Gallery berhasil dilike!'}, status=status.HTTP_201_CREATED)

class UnlikeGalleryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeGallery.objects.all()
    serializer_class = LikeGallerySerializer

    def destroy(self, request, gallery_pk, *args, **kwargs):
        account = request.user.account
        gallery = get_object_or_404(Gallery, pk=gallery_pk)

        try:
            like_instance = LikeGallery.objects.get(account=account, gallery=gallery)
            like_instance.delete()

            return Response({'detail': 'Gallery berhasil diunlike'}, status=status.HTTP_200_OK)
        except LikeGallery.DoesNotExist:
            return Response({'detail': 'Anda belum melakukan like pada gallery ini'}, status=status.HTTP_400_BAD_REQUEST)
        except Gallery.DoesNotExist:
            return Response({'detail': 'Gallery tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
        
class LikeArticleView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeArticle.objects.all()
    serializer_class = LikeArticleSerializer

    def create(self, request, article_pk, *args, **kwargs):
        account = request.user.account

        article = Article.objects.get(pk=article_pk)

        try:
            like_instance = LikeArticle.objects.get(account=account, article=article)
            return Response({'detail': 'Anda sudah malakukan like pada artikel ini'}, status=status.HTTP_400_BAD_REQUEST)
        except LikeArticle.DoesNotExist:
            LikeArticle.objects.create(account=account, article=article)
            return Response({'detail': 'Artikel berhasil dilike!'}, status=status.HTTP_201_CREATED)

class UnlikeArticleView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeArticle.objects.all()
    serializer_class = LikeArticleSerializer

    def destroy(self, request, article_pk, *args, **kwargs):
        account = request.user.account
        article = get_object_or_404(Article, pk=article_pk)

        try:
            like_instance = LikeArticle.objects.get(account=account, article=article)
            like_instance.delete()

            return Response({'detail': 'Artikel berhasil diunlike'}, status=status.HTTP_200_OK)
        except LikeArticle .DoesNotExist:
            return Response({'detail': 'Anda belum melakukan like pada artikel ini'}, status=status.HTTP_400_BAD_REQUEST)
        except Article.DoesNotExist:
            return Response({'detail': 'Artikel tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

class GetLikeVideoView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeVideo.objects.all()
    serializer_class = LikeVideoSerializer

    def get_queryset(self):
        account = self.request.user.account
        return LikeVideo.objects.filter(account=account)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetLikeGalleryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeGallery.objects.all()
    serializer_class = LikeGallerySerializer

    def get_queryset(self):
        account = self.request.user.account
        return LikeGallery.objects.filter(account=account)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetLikeArticleView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = LikeArticle.objects.all()
    serializer_class = LikeArticleSerializer

    def get_queryset(self):
        account = self.request.user.account
        return LikeArticle.objects.filter(account=account)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)