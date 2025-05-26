from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('siswa', 'Siswa'),
        ('guru', 'Guru'),
    ]
    nama = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES)
    foto_profil = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nama']

    def __str__(self):
        return f"{self.nama} ({self.get_role_display()})"


class Kelas(models.Model):
    nama_kelas = models.CharField(max_length=100)
    mata_pelajaran = models.CharField(max_length=100)
    kode_kelas = models.CharField(max_length=20, unique=True)
    guru = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'guru'},
        related_name='kelas_yang_diajar'
    )

    def __str__(self):
        return f"{self.nama_kelas} - {self.mata_pelajaran}"


class Tugas(models.Model):
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField()
    deadline = models.DateTimeField()
    kelas = models.ForeignKey(
        Kelas,
        on_delete=models.CASCADE,
        related_name='tugas'
    )

    def __str__(self):
        return f"{self.judul} (Kelas: {self.kelas.nama_kelas})"


class PengumpulanTugas(models.Model):
    siswa = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'siswa'},
        related_name='pengumpulan_tugas'
    )
    tugas = models.ForeignKey(
        Tugas,
        on_delete=models.CASCADE,
        related_name='pengumpulan'
    )
    file = models.FileField(upload_to='submissions/')
    waktu_pengumpulan = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('siswa', 'tugas')

    def __str__(self):
        return f"{self.siswa.nama} - {self.tugas.judul}"


class Komentar(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='komentar'
    )
    tugas = models.ForeignKey(
        Tugas,
        on_delete=models.CASCADE,
        related_name='komentar'
    )
    isi = models.TextField()
    waktu = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Komentar oleh {self.user.nama} pada {self.tugas.judul}"


class Nilai(models.Model):
    pengumpulan = models.OneToOneField(
        PengumpulanTugas,
        on_delete=models.CASCADE,
        related_name='nilai'
    )
    guru = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'guru'},
        related_name='penilaian'
    )
    nilai = models.DecimalField(max_digits=5, decimal_places=2)
    komentar = models.TextField(blank=True)

    def __str__(self):
        return f"Nilai {self.nilai} oleh {self.guru.nama}"


class SiswaKelas(models.Model):
    siswa = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'siswa'},
        related_name='kelas_diikuti'
    )
    kelas = models.ForeignKey(
        Kelas,
        on_delete=models.CASCADE,
        related_name='peserta'
    )

    class Meta:
        unique_together = ('siswa', 'kelas')

    def __str__(self):
        return f"{self.siswa.nama} di {self.kelas.nama_kelas}"
