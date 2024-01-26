from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-KEY')
        return api_key == settings.API_KEY
    
class IsOwnerOrManagerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
    
        return obj.channel.account == request.user.account or obj.channel.manager.filter(account_manager=request.user.account).exists()