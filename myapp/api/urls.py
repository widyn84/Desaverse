from django.urls import path, include
from rest_framework.authtoken import views as AuthTokenView
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.conf.urls.static import static
from django.conf import settings
from .views import CustomObtainAuthToken
from django.contrib import admin

from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('token/',  CustomObtainAuthToken.as_view(), name='user-signin'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('create-user/', views.CreateUserView.as_view({'post': 'create'}), name='create-user'),
    path('verify-email/', views.VerifyEmailViewSet.as_view({'post': 'create'}), name='verify-email'),
    path('accounts/', views.ListAccountView.as_view({'get': 'list'}), name='get-channel-retrieve'),
    path('accounts/<int:pk>/', views.ListAccountView.as_view({'get': 'retrieve'}), name='list-channel'),
    path('account/', views.GetDetailAccountView.as_view({'get': 'list'}), name='account-detail'),
    path('account/update/', views.UpdateAccountView.as_view({'put': 'update'}), name='account-update'),
    path('account-update-admin/<int:pk>/', views.UpdateAccountAdminView.as_view({'patch': 'partial_update'}), name='account-update-admin'),
    path('account/change-password/', views.ChangePasswordViewSet.as_view({'post': 'create'}), name='change_password'),
    path('change-password-admin/<int:pk>/', views.ChangePasswordAdminViewSet.as_view({'post': 'create'}), name='change-password-admin'),
    path('account/delete/', views.UserDeleteView.as_view({'delete': 'destroy'}), name='delete-user'),
    path('account-delete-admin/<int:pk>/', views.UserDeleteAdminViewSet.as_view({'delete': 'destroy'}), name='delete-user-admin'),
    path('create-channel/', views.CreateChannelView.as_view({'post': 'create'}), name='create-channel'),
    path('create-manager-channel/', views.CreateManagerChannelView.as_view({'post': 'create'}), name='create-manager-channel'),
    path('delete-manager-channel/<int:account_id>/', views.DeleteManagerChannelView.as_view({'delete': 'destroy'}), name='delete-manager-channel'),
    path('channels/', views.ListChannelView.as_view({'get': 'list'}), name='list-channel'),
    path('channels/<int:pk>/', views.GetChannelRetrieveView.as_view({'get': 'retrieve'}), name='channel-retrieve'),
    path('channel/', views.GetDetailChannelView.as_view({'get': 'list'}), name='channel-detail'),
    path('channel/update/', views.UpdateChannelView.as_view({'patch': 'partial_update'}), name='channel-update'),
    path('channel/delete/', views.DeleteChannelView.as_view({'delete': 'destroy'}), name='channel-delete'),
    path('channels/<int:pk>/videos/', views.GetListVideoChannelView.as_view({'get': 'list'}), name='list-video-channel'),
    path('channels/<int:channel_pk>/videos/<int:video_pk>/', views.GetVideoRetrieveView.as_view({'get': 'retrieve'}), name='video-retrieve'),
    path('videos/', views.GetListVideosView.as_view({'get': 'list'}), name='list-video'),
    path('create-video/', views.CreateVideoView.as_view({'post': 'create'}), name='create-video'),
    path('channel/video/<int:video_pk>/update/', views.UpdateVideoView.as_view({'patch': 'partial_update'}), name='update-video'),
    path('channel/video/<int:video_pk>/delete/', views.DeleteVideoView.as_view({'delete': 'destroy'}), name='delete-video'),
    path('create-gallery/', views.CreateGalleryView.as_view({'post': 'create'}), name='create-gallery'),
    path('channels/<int:pk>/gallery/', views.GetListGalleryChannelView.as_view({'get': 'list'}), name='list-gallery-channel'),
    path('channels/<int:channel_pk>/gallery/<int:gallery_pk>/', views.GetGalleryRetrieveView.as_view({'get': 'retrieve'}), name='gallery-retrieve'),
    path('galleries/', views.GetListGalleriesView.as_view({'get': 'list'}), name='list-video'),
    path('channel/gallery/<int:gallery_pk>/update/', views.UpdateGalleryView.as_view({'patch': 'partial_update'}), name='update-gallery'),
    path('channel/gallery/<int:gallery_pk>/delete/', views.DeleteGalleryView.as_view({'delete': 'destroy'}), name='delete-video'),
    path('create-article/', views.CreateArticleView.as_view({'post': 'create'}), name='create-article'),
    path('articles/', views.GetListArticlesView.as_view({'get': 'list'}), name='list-article'),
    path('channels/<int:pk>/article/', views.GetListArticleChannelView.as_view({'get': 'list'}), name='list-article-channel'),
    path('channels/<int:channel_pk>/article/<int:article_pk>/', views.GetArticleRetrieveView.as_view({'get': 'retrieve'}), name='article-retrieve'),
    path('channel/article/<int:article_pk>/update/', views.UpdateArticleView.as_view({'patch': 'partial_update'}), name='update-article'),
    path('channel/article/<int:article_pk>/delete/', views.DeleteArticleView.as_view({'delete': 'destroy'}), name='delete -article'),
    path('create-verification-channel/', views.CreateVerificationChannelView.as_view({'post': 'create'}), name='create-verification-channel'),
    path('update-status-channel/<int:pk>/', views.UpdateStatusVerificationView.as_view({'patch': 'partial_update'}), name='update-status-channel'),
    path('list-verification-channel-admin/', views.GetListVerificationAdminView.as_view({'get': 'list'}), name='list-verification-channel-admin'),
    path('list-verification-channel-admin/<int:pk>/', views.GetListVerificationAdminRetrieveView.as_view({'get': 'retrieve'}), name='list-verification-channel-admin-retrieve'),
    path('list-verification-channel-user/', views.GetListVerificationUserView.as_view({'get': 'list'}), name='list-verification-channel-user'),
    path('delete-verification-channel-user/<int:pk>/', views.DeleteVerificationUserView.as_view({'delete': 'destroy'}), name='delete-verification-channel-user'),
    path('review-video/<int:pk>/', views.ReviewVideoView.as_view({'patch': 'partial_update'}), name='review-video'),
    path('review-gallery/<int:pk>/', views.ReviewGalleryView.as_view({'patch': 'partial_update'}), name='review-gallery'),
    path('review-article/<int:pk>/', views.ReviewArticleView.as_view({'patch': 'partial_update'}), name='review-article'),
    path('like-video/<int:video_pk>/', views.LikeVideoView.as_view({'post': 'create'}), name='like-video'),
    path('unlike-video/<int:video_pk>/', views.UnlikeVideoView.as_view({'delete': 'destroy'}), name='unlike-video'),
    path('like-gallery/<int:gallery_pk>/', views.LikeGalleryView.as_view({'post': 'create'}), name='like-gallery'),
    path('unlike-gallery/<int:gallery_pk>/', views.UnlikeGalleryView.as_view({'delete': 'destroy'}), name='unlike-gallery'),
    path('like-article/<int:article_pk>/', views.LikeArticleView.as_view({'post': 'create'}), name='like-article'),
    path('unlike-article/<int:article_pk>/', views.UnlikeArticleView.as_view({'delete': 'destroy'}), name='unlike-article '),
    path('like-video-retrieve/', views.GetLikeVideoView.as_view({'get': 'list'}), name='get-like-video'),    
    path('like-gallery-retrieve/', views.GetLikeGalleryView.as_view({'get': 'list'}), name='get-like-gallery'),    
    path('like-article-retrieve/', views.GetLikeArticleView.as_view({'get': 'list'}), name='get-like-article'),    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)