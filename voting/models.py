from django.db import models
from django.shortcuts import render, redirect

class Voter(models.Model):
    name = models.CharField(max_length=100)
    epic_number = models.CharField(max_length=20, unique=True)
    aadhaar_number = models.CharField(max_length=12, unique=True)
    phone = models.CharField(max_length=15)
    constituency = models.CharField(max_length=100)  # ✅ ADD THIS
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    party = models.CharField(max_length=255)
    constituency = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.party})"

class Vote(models.Model):
    voter = models.OneToOneField(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # 🔥 important

    def __str__(self):
        return f"{self.voter} voted for {self.candidate}"


class Election(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ElectionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    success_count = models.IntegerField()
    failed_count = models.IntegerField(default=0)
    file_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Log at {self.timestamp}: {self.success_count} successes, {self.failed_count} failures"