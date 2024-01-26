from django.contrib import admin

from .models import *

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id','user','foto_account','type_account','deskripsi_account','no_telpon', 'email_verified', 'created', 'updated']
    fields = ['user', 'foto_account', 'type_account', 'deskripsi_account', 'no_telpon', 'email_verified']
    list_filter = ['user', ]

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'nama_channel', 'akronim', 'deskripsi', 'logo', 'daerah', 'alamat','isActive', 'isModerated',  'created', 'updated',]
    exclude = ['created', 'updated']
    list_filter = ['account', 'nama_channel']

@admin.register(ManagerChannel)
class ManagerChannelADmin(admin.ModelAdmin):
    list_display = ['id', 'account_manager', 'channel', 'start_managing', 'end_managing']
    list_filter = ['account_manager', 'channel']

@admin.register(ChannelVerification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'channel', 'foto_ktp', 'surat_keterangan', 'status_verifikasi', 'pesan', 'created', 'updated']
    exclude = ['created', 'updated']
    list_filter = ['channel']

@admin.register(ContentVideo)
class ContentVideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'channel', 'judul_video', 'kategori_video', 'file_video', 'thumbnail', 'deskripsi', 'creator', 'updated_by', 'status', 'pesan_status', 'created', 'updated']
    exclude = ['created', 'updated']
    list_filter = ['channel', 'judul_video']

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['id', 'channel', 'kategori_galeri', 'foto', 'deskripsi', 'creator', 'updated_by', 'status', 'pesan_status',  'created', 'updated']
    exclude = ['created', 'updated']
    list_filter = ['channel']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'channel', 'kategori_artikel', 'judul_artikel', 'cover_artikel', 'creator', 'updated_by', 'status', 'pesan_status',  'created', 'updated']
    exclude = ['created', 'updated']
    list_filter = ['channel', 'judul_artikel']

@admin.register(LikeVideo)
class LikeVideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'video', 'created']
    exclude = ['created', ]
    list_filter = ['video']

@admin.register(LikeGallery)
class LikeGalleryAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'gallery', 'created']
    exclude = ['created', ]
    list_filter = ['gallery']

@admin.register(LikeArticle)
class LikeGalleryAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'article', 'created']
    exclude = ['created', ]
    list_filter = ['article']
