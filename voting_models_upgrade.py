# =====================================================
# DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM MODELS
# =====================================================

from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models import Sum, Max, F
from django.utils import timezone

class PollingStation(models.Model):
    """Existing model - assuming it exists"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    ward = models.ForeignKey('Ward', on_delete=models.CASCADE)
    constituency = models.ForeignKey('Constituency', on_delete=models.CASCADE)
    county = models.ForeignKey('County', on_delete=models.CASCADE)
    registered_voters = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Polling Station"
        verbose_name_plural = "Polling Stations"

class VotingSession(models.Model):
    """NEW: Manage election sessions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Voting Session"
        verbose_name_plural = "Voting Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

class Result(models.Model):
    """NEW: Core results table - CRITICAL REQUIREMENT"""
    polling_station = models.ForeignKey(PollingStation, on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    votes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of votes received at this polling station"
    )
    voting_session = models.ForeignKey(VotingSession, on_delete=models.CASCADE, default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Election Result"
        verbose_name_plural = "Election Results"
        unique_together = ('polling_station', 'candidate', 'voting_session')  # Prevent duplicates
        ordering = ['-votes']
    
    def __str__(self):
        return f"{self.candidate} - {self.votes} votes at {self.polling_station}"
    
    def clean(self):
        """Validate result entry"""
        if self.votes < 0:
            raise ValidationError("Votes cannot be negative")
        
        # Validate candidate belongs to the correct area for this polling station
        candidate = self.candidate
        station = self.polling_station
        
        if candidate.position.name == 'MCA' and candidate.ward != station.ward:
            raise ValidationError("MCA candidate must belong to the same ward as polling station")
        elif candidate.position.name == 'MP' and candidate.constituency != station.constituency:
            raise ValidationError("MP candidate must belong to the same constituency as polling station")
        elif candidate.position.name in ['Governor', 'Senator', 'WOMEN_REP'] and candidate.county != station.county:
            raise ValidationError(f"{candidate.position.name} candidate must belong to the same county as polling station")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Trigger aggregation update
        self.update_aggregated_results()
    
    def update_aggregated_results(self):
        """Update aggregated results when result changes"""
        from .tasks import update_candidate_aggregation
        update_candidate_aggregation.delay(self.candidate.id)

class AggregatedResult(models.Model):
    """NEW: Cache for aggregated results - PERFORMANCE OPTIMIZATION"""
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    area_type = models.CharField(
        max_length=20,
        choices=[
            ('county', 'County'),
            ('constituency', 'Constituency'),
            ('ward', 'Ward')
        ]
    )
    area_id = models.IntegerField()
    total_votes = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Aggregated Result"
        verbose_name_plural = "Aggregated Results"
        unique_together = ('candidate', 'position', 'area_type', 'area_id')
        indexes = [
            models.Index(fields=['candidate', 'position', 'area_type', 'area_id']),
            models.Index(fields=['area_type', 'area_id']),
            models.Index(fields=['total_votes']),
        ]
    
    def __str__(self):
        return f"{self.candidate} - {self.total_votes} votes in {self.area_type} {self.area_id}"

class ResultBackup(models.Model):
    """NEW: Audit trail for result changes"""
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    polling_station = models.ForeignKey(PollingStation, on_delete=models.CASCADE)
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    votes = models.IntegerField()
    action_type = models.CharField(
        max_length=20,
        choices=[
            ('CREATE', 'Create'),
            ('UPDATE', 'Update'),
            ('DELETE', 'Delete')
        ]
    )
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Result Backup"
        verbose_name_plural = "Result Backups"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action_type}: {self.candidate} - {self.votes} votes by {self.performed_by}"

# RESULT MANAGER - CUSTOM QUERY METHODS
class ResultManager(models.Manager):
    """Custom manager for result queries and aggregations"""
    
    def get_mca_results_by_ward(self, ward_id):
        """Aggregate MCA results by ward"""
        return self.filter(
            candidate__position__name='MCA',
            polling_station__ward_id=ward_id
        ).values(
            'candidate__id',
            'candidate__first_name',
            'candidate__last_name',
            'candidate__party__name'
        ).annotate(
            total_votes=Sum('votes')
        ).order_by('-total_votes')
    
    def get_mp_results_by_constituency(self, constituency_id):
        """Aggregate MP results by constituency"""
        return self.filter(
            candidate__position__name='MP',
            polling_station__constituency_id=constituency_id
        ).values(
            'candidate__id',
            'candidate__first_name',
            'candidate__last_name',
            'candidate__party__name'
        ).annotate(
            total_votes=Sum('votes')
        ).order_by('-total_votes')
    
    def get_county_results(self, county_id, position_name):
        """Aggregate county-level results"""
        return self.filter(
            candidate__position__name=position_name,
            polling_station__county_id=county_id
        ).values(
            'candidate__id',
            'candidate__first_name',
            'candidate__last_name',
            'candidate__party__name'
        ).annotate(
            total_votes=Sum('votes')
        ).order_by('-total_votes')
    
    def get_winner_for_area(self, area_type, area_id, position_name=None):
        """Determine winner for a specific area"""
        if area_type == 'ward' and position_name == 'MCA':
            results = self.get_mca_results_by_ward(area_id)
        elif area_type == 'constituency' and position_name == 'MP':
            results = self.get_mp_results_by_constituency(area_id)
        elif area_type == 'county' and position_name:
            results = self.get_county_results(area_id, position_name)
        else:
            return None
        
        return results.first() if results.exists() else None
    
    def get_participation_stats(self, area_type, area_id):
        """Calculate voter participation statistics"""
        if area_type == 'ward':
            stations = PollingStation.objects.filter(ward_id=area_id)
        elif area_type == 'constituency':
            stations = PollingStation.objects.filter(constituency_id=area_id)
        elif area_type == 'county':
            stations = PollingStation.objects.filter(county_id=area_id)
        else:
            return None
        
        total_registered = stations.aggregate(total=Sum('registered_voters'))['total'] or 0
        total_votes = self.filter(polling_station__in=stations).aggregate(total=Sum('votes'))['total'] or 0
        
        return {
            'registered_voters': total_registered,
            'total_votes_cast': total_votes,
            'turnout_percentage': (total_votes / total_registered * 100) if total_registered > 0 else 0
        }

# Add custom manager to Result model
Result.add_to_class('objects', ResultManager())

# WINNER DETERMINATION METHODS
class WinnerManager(models.Manager):
    """Manager for winner determination logic"""
    
    def get_winners_by_county(self, county_id):
        """Get all winners for a county"""
        winners = {}
        positions = ['Governor', 'Senator', 'WOMEN_REP']
        
        for position in positions:
            winner = Result.objects.get_winner_for_area('county', county_id, position)
            if winner:
                winners[position] = winner
        
        return winners
    
    def get_mp_winner_by_constituency(self, constituency_id):
        """Get MP winner for constituency"""
        return Result.objects.get_winner_for_area('constituency', constituency_id, 'MP')
    
    def get_mca_winner_by_ward(self, ward_id):
        """Get MCA winner for ward"""
        return Result.objects.get_winner_for_area('ward', ward_id, 'MCA')

class Winner(models.Model):
    """Cache for determined winners - PERFORMANCE OPTIMIZATION"""
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    position = models.ForeignKey('Position', on_delete=models.CASCADE)
    area_type = models.CharField(max_length=20)
    area_id = models.IntegerField()
    total_votes = models.IntegerField()
    margin_votes = models.IntegerField(default=0)  # Difference from second place
    determined_at = models.DateTimeField(auto_now_add=True)
    
    objects = WinnerManager()
    
    class Meta:
        verbose_name = "Election Winner"
        verbose_name_plural = "Election Winners"
        unique_together = ('position', 'area_type', 'area_id')
    
    def __str__(self):
        return f"{self.candidate} - Winner for {self.area_type} {self.area_id}"
