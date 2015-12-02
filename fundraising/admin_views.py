import csv

from django.http import HttpResponse

from .models import Payment


def download_donor_report(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donor-report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'name',
        'email',
        'alternate email',
        'last gift date',
        'gift amount (US$)',
        'interval',
        'recurring active?',
        'location',
    ])
    for donor in queryset:
        last_payment = Payment.objects.filter(donation__donor=donor).select_related('donation').latest('date')
        last_gift = last_payment.donation
        last_gift_date = last_payment.date.date()
        last_gift_amount = last_payment.amount
        primary_email = donor.email if donor.email else last_gift.receipt_email
        # Include the receipt_email from Stripe if it's different from the
        # primary email.
        if primary_email and last_gift.receipt_email.lower() != primary_email.lower():
            alternate_email = last_gift.receipt_email
        else:
            alternate_email = ''
        writer.writerow([
            donor.name,
            primary_email,
            alternate_email,
            last_gift_date,
            last_gift_amount,
            last_gift.get_interval_display().replace('donation', ''),
            'Yes' if last_gift.stripe_subscription_id else '',
            donor.location,
        ])
    return response
