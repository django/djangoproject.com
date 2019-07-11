from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.dateformat import format as date_format
from djmoney.models.fields import MoneyField
from docutils.core import publish_parts

from blog.models import BLOG_DOCUTILS_SETTINGS


class Office(models.Model):
    """
    An office held by a DSF Board member.

    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Term(models.Model):
    """
    A term in which DSF Board members served.

    """
    year = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.year


class BoardMember(models.Model):
    """
    A DSF Board member.

    """
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    office = models.ForeignKey(
        Office, related_name='holders', on_delete=models.CASCADE
    )
    term = models.ForeignKey(
        Term, related_name='board_members', on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} ({} - {})".format(
            self.account.get_full_name(), self.office, self.term.year)


class NonBoardAttendee(models.Model):
    """
    A non-Board member attending a Board meeting.

    """
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Non-board attendee'
        verbose_name_plural = 'Non-board attendees'

    def __str__(self):
        return "{} ({})".format(self.name, self.role)


class Meeting(models.Model):
    """
    A meeting of the DSF Board.

    """
    date = models.DateField()
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    leader = models.ForeignKey(BoardMember, related_name='meetings_led', on_delete=models.CASCADE)
    board_attendees = models.ManyToManyField(BoardMember, related_name='meetings_attended')
    non_board_attendees = models.ManyToManyField(
        NonBoardAttendee, related_name='meetings_attended', blank=True
    )
    treasurer_balance = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD',
        default=Decimal('0.0'),
    )
    treasurer_report = models.TextField(blank=True)
    treasurer_report_html = models.TextField(editable=False)

    def __str__(self):
        return "{}, {}".format(
            self.title, date_format(self.date, "F j, Y")
        )

    def save(self, *args, **kwargs):
        if self.treasurer_report:
            self.treasurer_report_html = publish_parts(
                source=self.treasurer_report, writer_name='html',
                settings_overrides=BLOG_DOCUTILS_SETTINGS
            )['fragment']
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'foundation_meeting_detail',
            args=(),
            kwargs={
                'year': self.date.strftime('%Y'),
                'month': self.date.strftime('%b').lower(),
                'day': self.date.strftime('%d'),
                'slug': self.slug
            }
        )


class ApprovedGrant(models.Model):
    """
    A grant approved by the DSF Board.

    """
    entity = models.CharField(max_length=255)
    amount = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD',
        default=Decimal('0.0'),
    )
    approved_at = models.ForeignKey(
        Meeting, related_name='grants_approved', on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('entity',)

    def __str__(self):
        return "{}: {}".format(self.entity, self.amount)


class ApprovedIndividualMember(models.Model):
    """
    An individual DSF member approved by the Board.

    """
    name = models.CharField(max_length=255)
    approved_at = models.ForeignKey(
        Meeting, related_name='individual_members_approved', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class ApprovedCorporateMember(models.Model):
    """
    A corporate DSF member approved by the Board.

    """
    name = models.CharField(max_length=255)
    approved_at = models.ForeignKey(
        Meeting, related_name='corporate_members_approved', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Business(models.Model):
    """
    Business of the DSF Board.

    """
    NEW = 'new'
    ONGOING = 'ongoing'

    TYPE_CHOICES = (
        (NEW, 'New'),
        (ONGOING, 'Ongoing'),
    )

    title = models.CharField(max_length=255)
    body = models.TextField()
    body_html = models.TextField(editable=False)
    business_type = models.CharField(max_length=25, choices=TYPE_CHOICES)
    meeting = models.ForeignKey(
        Meeting, related_name='business', on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Business'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.body_html = publish_parts(
            source=self.body, writer_name='html',
            settings_overrides=BLOG_DOCUTILS_SETTINGS
        )['fragment']
        super().save(*args, **kwargs)


class ActionItem(models.Model):
    """
    A task to be completed by an attendee of a DSF Board meeting.

    """
    responsible = models.CharField(max_length=255)
    task = models.TextField()
    meeting = models.ForeignKey(
        Meeting, related_name='action_items', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.task
