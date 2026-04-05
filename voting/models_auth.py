from django.contrib.auth.models import AbstractUser
from django.db import models

class ElectoralUser(AbstractUser):
    """Custom user model for Kenya Electoral Management System"""
    
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('iebc_official', 'IEBC Official'),
        ('county_officer', 'County Election Officer'),
        ('constituency_officer', 'Constituency Officer'),
        ('ward_officer', 'Ward Officer'),
        ('observer', 'Election Observer'),
        ('public', 'Public User'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='public')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    county = models.ForeignKey('voting.County', on_delete=models.SET_NULL, null=True, blank=True)
    constituency = models.ForeignKey('voting.Constituency', on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'electoral_users'
        verbose_name = 'Electoral User'
        verbose_name_plural = 'Electoral Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def has_county_access(self, county):
        """Check if user has access to specific county"""
        if self.role in ['admin', 'iebc_official']:
            return True
        return self.county == county
    
    def has_constituency_access(self, constituency):
        """Check if user has access to specific constituency"""
        if self.role in ['admin', 'iebc_official']:
            return True
        if self.role == 'county_officer' and self.county == constituency.county:
            return True
        return self.constituency == constituency
    
    def get_accessible_counties(self):
        """Get list of counties user can access"""
        if self.role in ['admin', 'iebc_official']:
            from voting.models import County
            return County.objects.all()
        if self.county:
            return [self.county]
        return []
    
    def get_accessible_constituencies(self):
        """Get list of constituencies user can access"""
        if self.role in ['admin', 'iebc_official']:
            from voting.models import Constituency
            return Constituency.objects.all()
        if self.role == 'county_officer' and self.county:
            return self.county.constituency_set.all()
        if self.constituency:
            return [self.constituency]
        return []

class UserSession(models.Model):
    """Track user sessions for security"""
    user = models.ForeignKey(ElectoralUser, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'

class AuditLog(models.Model):
    """Audit log for tracking system activities"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(ElectoralUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    changes = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"
