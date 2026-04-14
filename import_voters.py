import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from voting.models import Voter

with open("voters.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        Voter.objects.create(
            name=row["name"],
            epic_number=row["epic_number"],
            aadhaar_number=row["aadhaar_number"],
            phone=row["phone"],
            constituency=row["constituency"]
        )

print("Voters imported successfully")