# -*- coding: utf-8 -*-
from django.db import models, migrations
import datetime

def assign_past_donation_and_testimonials_to_campaign(apps, schema_editor):
    Campaign = apps.get_model("fundraising", "Campaign")
    Donation = apps.get_model("fundraising", "Donation")
    Testimonial = apps.get_model("fundraising", "Testimonial")

    # create first campaign
    campaign = Campaign.objects.create(
        name = "Django Fellowship",
        slug = "django-fellowship",
        goal = 30000,
        stretch_goal = 50000,
        stretch_goal_url = "https://www.djangoproject.com/weblog/2015/jan/27/django-fellowship-fundraising-goal-achieved/",
        start_date = datetime.datetime(2015,1,21,0,0,0),
        end_date = datetime.datetime(2015,2,28,0,0,0),
        is_active = True,
        is_public = True
    )

    for donation in Donation.objects.all():
        donation.campaign = campaign
        donation.save()

    for testimonial in Testimonial.objects.all():
        testimonial.campaign = campaign
        testimonial.save()

class Migration(migrations.Migration):

    dependencies = [
        ('fundraising', '0018_auto_20150209_1424'),
    ]

    operations = [
        migrations.RunPython(assign_past_donation_and_testimonials_to_campaign),
    ]
