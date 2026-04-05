from django.db import models

class County(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Constituency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=150, unique=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.county.name}"

class Ward(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=150, unique=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    registered_voters_2022 = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.constituency.name}"

class PollingCenter(models.Model):
    name = models.CharField(max_length=200)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='polling_centers')
    code = models.CharField(max_length=10, unique=True)
    registered_voters = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.ward.name}"

class PollingStation(models.Model):
    name = models.CharField(max_length=200)
    polling_center = models.ForeignKey(PollingCenter, on_delete=models.CASCADE, related_name='polling_stations')
    code = models.CharField(max_length=10, unique=True)
    registered_voters = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.polling_center.name}"
