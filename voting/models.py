from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from smart_selects.db_fields import ChainedForeignKey
from django.utils import timezone
import random
import string


class Party(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='party_logos/')
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Parties"


class County(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Counties"


class Constituency(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    code = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return f"{self.name} - {self.county.name}"

    class Meta:
        verbose_name_plural = "Constituencies"


class Ward(models.Model):
    name = models.CharField(max_length=100)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    # Electoral Statistics
    registered_voters_2022 = models.IntegerField(default=0)
    polling_centers = models.IntegerField(default=0)
    polling_stations = models.IntegerField(default=0)
    avg_voters_per_center = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    avg_voters_per_station = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} - {self.constituency.name}"


class PollingCenter(models.Model):
    name = models.CharField(max_length=100)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    registered_voters = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.ward.name}"


class PollingStation(models.Model):
    name = models.CharField(max_length=100)
    center = models.ForeignKey(
        PollingCenter, on_delete=models.CASCADE, related_name='polling_stations')
    code = models.CharField(max_length=10, unique=True)
    registered_voters = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.center.name}"


class Position(models.Model):
    POSITION_CHOICES = [
        ('PRESIDENT', 'President'),
        ('GOVERNOR', 'Governor'),
        ('SENATOR', 'Senator'),
        ('WOMEN_REP', 'Women Representative'),
        ('MP', 'Member of Parliament'),
        ('MCA', 'Member of County Assembly'),
    ]

    name = models.CharField(
        max_length=20, choices=POSITION_CHOICES, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.get_name_display()


class Candidate(models.Model):
    id_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidate_photos/')
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    county = models.ForeignKey(
        County, on_delete=models.CASCADE, null=True, blank=True)
    constituency = ChainedForeignKey(
        Constituency,
        chained_field="county",
        chained_model_field="county",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True
    )
    ward = ChainedForeignKey(
        Ward,
        chained_field="constituency",
        chained_model_field="constituency",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"

    def save(self, *args, **kwargs):
        if self.position.name == 'PRESIDENT':
            self.county = None
            self.constituency = None
            self.ward = None
        elif self.position.name == 'GOVERNOR' or self.position.name == 'SENATOR' or self.position.name == 'WOMEN_REP':
            self.constituency = None
            self.ward = None
        elif self.position.name == 'MP':
            self.ward = None
        super().save(*args, **kwargs)


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, unique=True)
    phone_number = PhoneNumberField(region='KE')
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    constituency = ChainedForeignKey(
        Constituency,
        chained_field="county",
        chained_model_field="county",
        show_all=False,
        auto_choose=True
    )
    ward = ChainedForeignKey(
        Ward,
        chained_field="constituency",
        chained_model_field="constituency",
        show_all=False,
        auto_choose=True
    )
    polling_center = ChainedForeignKey(
        PollingCenter,
        chained_field="ward",
        chained_model_field="ward",
        show_all=False,
        auto_choose=True
    )
    polling_station = ChainedForeignKey(
        PollingStation,
        chained_field="polling_center",
        chained_model_field="center",
        show_all=False,
        auto_choose=True
    )
    is_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)

    def get_display_name(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        if full_name:
            return full_name
        if self.user.username:
            return self.user.username
        return f"Voter {self.id_number}"

    def __str__(self):
        return f"{self.get_display_name()} - {self.id_number}"


class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"

    def is_valid(self):
        # OTP is valid for 10 minutes
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 600

    @classmethod
    def generate_otp(cls, user):
        # Generate 6-digit random OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        # Mark any existing OTPs as used
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        # Create new OTP
        return cls.objects.create(user=user, otp_code=otp_code)


class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')

    def __str__(self):
        return f"{self.voter} - {self.position} - {self.timestamp}"
