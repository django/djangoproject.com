from django.db import models
from ..trac.models import Ticket

class PullRequest(models.Model):
    """
    A GitHub pull request.
    """
    # The pull request number - using this isntead of "id" to more closely
    # match the GitHub terminology.
    number = models.PositiveIntegerField(primary_key=True)
    ticket = models.ForeignKey(Ticket, related_name='pull_requests')
