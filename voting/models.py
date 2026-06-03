from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import hashlib

# Custom User Manager for Matric Number login
class StudentManager(BaseUserManager):
    def create_user(self, matric_number, password=None, **extra_fields):
        if not matric_number:
            raise ValueError('Matric number is required')
        
        user = self.model(matric_number=matric_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, matric_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(matric_number, password, **extra_fields)

class Student(AbstractBaseUser, PermissionsMixin):
    matric_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = StudentManager()
    
    USERNAME_FIELD = 'matric_number'
    REQUIRED_FIELDS = ['full_name']
    
    def __str__(self):
        return f"{self.matric_number} - {self.full_name}"

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    allowed_faculty = models.CharField(max_length=100, blank=True, null=True, help_text="Leave blank for university-wide elections")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ... rest of the model
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'
        elif self.start_time <= now <= self.end_time:
            return 'active'
        else:
            return 'closed'
    
    @property
    def total_votes(self):
        return Vote.objects.filter(election=self).count()
    
    class Meta:
        ordering = ['-created_at']

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='candidates/', blank=True, null=True)
    manifesto = models.TextField(blank=True)
    vote_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} ({self.position}) - {self.election.title}"

class Vote(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    vote_hash = models.CharField(max_length=64, unique=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'election']  # One vote per user per election
    
    def save(self, *args, **kwargs):
        # Generate fake security hash
        if not self.vote_hash:
            hash_string = f"{self.user.id}{self.election.id}{self.voted_at}"
            self.vote_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.matric_number} voted for {self.candidate.name}"