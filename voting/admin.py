from django.contrib import admin
from .models import Voter, Candidate, Vote

admin.site.register(Voter)
admin.site.register(Candidate)
admin.site.register(Vote)