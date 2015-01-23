"""
Track signed CLAs.
"""
from django.db import models
from django.contrib.auth.models import User


class ICLA(models.Model):
    """
    An individual's CLA.

    Since we have to deal with some legacy data this is a bit more tricky
    than it has to be. Ideally we'd relate each CLA to a User so we can
    see that info in Trac, but we've got a set of CLAs in paper/PDF form
    that need to be imported and related to individuals. Thus most fields
    here will have to be optional to accommodate this unclean data.

    As we switch to e-sign we'll make most of this stuff required at the
    *form* level, and clean up legacy data as we can. Eventually this'll
    get trimmed down to a more clean set of fields.
    """
    user = models.ForeignKey(User, related_name='iclas', blank=True, null=True)
    date_signed = models.DateField()
    cla = models.FileField(upload_to='cla', blank=True)

    # I'm not clear if all of these are actually required by law or anything,
    # but they're the fields on the CLA forms, so we'll include them here but
    # make them optional in case we choose to drop them in the future. These
    # *do* duplicate some of the fields on the user model, but copying them over
    # is a PITA so we don't for now.
    full_name = models.CharField(max_length=250, blank=True)
    email = models.EmailField(blank=True)
    nickname = models.CharField(max_length=250, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    mailing_address = models.TextField(blank=True)
    country = models.CharField(max_length=50, blank=True)

    class Meta(object):
        verbose_name = 'individual CLA'
        verbose_name_plural = 'individual CLAs'

    def __str__(self):
        return self.full_name or str(self.user)


class CCLA(models.Model):
    """
    A corporate CLA.

    Caveats are as above. However, we're a little stricter out of the box about
    CCLAs even with legacy data. Corporate contributions are a bit of a bigger
    deal legally, and we have fewer of them, so we'll be more careful.
    """
    # Required fields, as for iCLA.
    date_signed = models.DateField()
    cla = models.FileField(upload_to='cla')

    # These are duplicated in the cCLA form, but they're also rather important
    # to be easily accessible, so we'll make them required here.
    company_name = models.CharField(max_length=200)
    company_address = models.TextField(blank=True)
    country = models.CharField(max_length=50)
    contact_name = models.CharField(max_length=250)
    contact_email = models.EmailField()
    contact_title = models.CharField(max_length=200)
    telephone = models.CharField(max_length=50, blank=True)

    class Meta(object):
        verbose_name = 'corporate CLA'
        verbose_name_plural = 'corporate CLAs'

    def __str__(self):
        return self.company_name


class CCLADesignee(models.Model):
    """
    An individual whose contrbutions are covered by a CCLA.

    Again caveats as above. One additional wrinkle here is that ideally CCLA
    signers will *also* sign an ICLA; a future version of this app might
    want to enforce that.
    """
    ccla = models.ForeignKey(CCLA, related_name='designees')
    user = models.ForeignKey(User, related_name='+', blank=True, null=True)
    icla = models.ForeignKey(ICLA, related_name='+', blank=True, null=True)
    date_added = models.DateField()
    full_name = models.CharField(max_length=250, blank=True)
    email = models.EmailField(blank=True)
    nickname = models.CharField(max_length=250, blank=True)

    class Meta(object):
        verbose_name = 'CCLA designee'
        verbose_name_plural = 'CCLA designees'

    def __str__(self):
        return self.full_name or str(self.user)


def find_agreements(user):
    """
    Find any CLAs covering the given user.

    Returns a list of ICLA/CCLADesignee objects covering the given user.
    """
    return list(ICLA.objects.filter(user=user)) + list(CCLADesignee.objects.filter(user=user))
