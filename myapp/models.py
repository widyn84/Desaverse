from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils import timezone
from datetime import timedelta
import os

def user_directory_path(instance, filename):
    safe_filename = os.path.basename(filename)
    return instance.get_upload_path(safe_filename)

from random import randint

def IntDefault():
    n = 8
    for_id = ''.join(["{}".format(randint(0, 9)) for num in range(0, n)])
    return for_id

class Account(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    ACCOUNT_CHOICE = [
        ("ADMIN", "ADMIN"),
        ("PUBLIC", "PUBLIC"),
        ("VERIFIKATOR", "VERIFIKATOR"),
        ("CHANNEL", "CHANNEL"),
        ("CHANNEL MANAGER", "CHANNEL MANAGER"),
        ("REVIEWER", "REVIEWER")
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    foto_account = models.ImageField(upload_to=user_directory_path, default="assets/image.svg")
    type_account = models.CharField(
        max_length=20,
        choices=ACCOUNT_CHOICE,
        default="PUBLIC",
    )
    deskripsi_account = models.TextField(max_length=40000, blank=True, null=True)
    no_telpon = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    def get_upload_path(self, filename):
        safe_filename = os.path.basename(filename)
        return f"assets/account-{self.id}/{safe_filename}"
   
class Channel(models.Model):    
    id = models.IntegerField(primary_key=True, default=IntDefault)
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='owner', null=False, blank=False)
    nama_channel = models.TextField(max_length=500, blank=False, null=False, unique=True)
    akronim = models.TextField(max_length=100, blank=False, null=False)
    deskripsi = models.TextField(max_length=40000, blank=True, null=True)
    logo = models.ImageField(upload_to=user_directory_path, default="assets/default-logo-channel.svg")
    isActive = models.BooleanField(default=False)
    isModerated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    daerah = models.CharField(max_length=500, blank=True, null=True)
    alamat = models.CharField(max_length=500, blank=True, null=True)
        
    def get_upload_path(self, filename):
        safe_filename = os.path.basename(filename)
        return f"assets/channel-{self.id}/{safe_filename}"
    
    def __str__(self):
        return self.nama_channel

class ManagerChannel(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    account_manager = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='manager', null=False, blank=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_managed', null=False, blank=False)
    start_managing = models.DateTimeField(null=True, blank=True)
    end_managing = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

        
class ChannelVerification(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_verification')
    foto_ktp = models.FileField(upload_to=user_directory_path, blank=False, null=False)
    surat_keterangan = models.FileField(upload_to=user_directory_path, blank=False, null=False)
    STATUS_CHOICE = [
        ("pending", "Menunggu Diverifikasi"),
        ("verified", "Berhasil Diverifikasi"),
        ("rejected", "Gagal Diverifikasi"),
    ]
    status_verifikasi = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending",
    )
    pesan = models.TextField(max_length=40000, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_upload_path(self, filename):
        safe_filename = os.path.basename(filename)
        return f"assets/channel-{self.channel.id}/verification/{safe_filename}"

class ContentVideo(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_videos')
    judul_video = models.TextField(max_length=1000, blank=False, null=False)
    KATEGORI_CHOICE = [
        ("UMKM", "UMKM"),
        ("Pertanian", "Pertanian"),
        ("Kesenian", "Kesenian"),
        ("Pariwisata", "Pariwisata"),
        ("Daerah", "Daerah"),
    ]
    STATUS_CHOICE = [
        ("pending", "Menunggu Direview"),
        ("accepted", "Diterima"),
        ("rejected", "Ditolak"),
    ]
    kategori_video = models.CharField(
        max_length= 20,
        choices=KATEGORI_CHOICE,
        default="Daerah"
    )
    file_video = models.FileField(upload_to=user_directory_path, blank=False, null=False)
    thumbnail = models.ImageField(upload_to=user_directory_path, default="assets/thumbnail.svg")
    deskripsi = models.TextField(max_length=40000, blank=True, null=True)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='creator')
    updated_by = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_video')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending",
    )
    pesan_status = models.TextField(max_length=40000, blank=True, null=True)
    liked_by = models.ManyToManyField(Account, through='LikeVideo', related_name='liked_videos')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def get_upload_path(self, filename):
        safe_filename = os.path.basename(filename)
        return f"assets/channel-{self.channel.id}/video/{safe_filename}"
    
    def __str__(self):
        return f"{self.channel.nama_channel} - {self.judul_video}"

class Gallery(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_galery')
    KATEGORI_CHOICE = [
        ("UMKM", "UMKM"),
        ("Pertanian", "Pertanian"),
        ("Kesenian", "Kesenian"),
        ("Pariwisata", "Pariwisata"),
        ("Daerah", "Daerah"),
    ]
    STATUS_CHOICE = [
        ("pending", "Menunggu Direview"),
        ("accepted", "Diterima"),
        ("rejected", "Ditolak"),
    ]
    kategori_galeri = models.CharField(
        max_length = 20,
        choices=KATEGORI_CHOICE,
        default="Daerah"
    )
    foto = models.ImageField(upload_to=user_directory_path, blank=False, null=False)
    deskripsi = models.TextField(max_length=40000, blank=True, null=True)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='creator_gallery')
    updated_by = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_gallery')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending",
    )
    pesan_status = models.TextField(max_length=40000, blank=True, null=True)
    liked_by = models.ManyToManyField(Account, through='LikeGallery', related_name='liked_galleries')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_upload_path(self, filename):
        safe_filename = os.path.basename(filename)
        return f"assets/channel-{self.channel.id}/gallery/{safe_filename}"
    
    def __str__(self):
        return f"{self.channel.nama_channel} - {self.deskripsi}"
    
class Article(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_article')
    KATEGORI_CHOICE = [
        ("UMKM", "UMKM"),
        ("Pertanian", "Pertanian"),
        ("Kesenian", "Kesenian"),
        ("Pariwisata", "Pariwisata"),
        ("Daerah", "Daerah"),
    ]
    STATUS_CHOICE = [
        ("pending", "Menunggu Direview"),
        ("accepted", "Diterima"),
        ("rejected", "Ditolak"),
    ]
    kategori_artikel = models.CharField(
        max_length=20,
        choices=KATEGORI_CHOICE,
        default="Daerah"
    )
    judul_artikel = models.TextField(max_length=1000, blank=False, null=False)
    cover_artikel = models.ImageField(upload_to=user_directory_path, blank=False, null=False)
    konten_artikel = RichTextField(blank=False, null=False)
    creator = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='creator_article')
    updated_by = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_article')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending",
    )
    pesan_status = models.TextField(max_length=40000, blank=True, null=True)
    liked_by = models.ManyToManyField(Account, through='LikeArticle', related_name='liked_article')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_upload_path(self, filename):
        self_filename = os.path.basename(filename)
        return f"assets/channel-{self.channel.id}/article/{self_filename}"
    
    def __str__(self):
        return f"{self.channel.nama_channel} - {self.judul_artikel}"

class LikeVideo(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    video = models.ForeignKey(ContentVideo, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class LikeGallery(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class LikeArticle(models.Model):
    id = models.IntegerField(primary_key=True, default=IntDefault)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
