import logging

import stripe
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **kwargs):
        try:
            stripe.Plan.retrieve("monthly")
            print("Monthly plan exists, not creating!")
        except stripe.error.InvalidRequestError:
            name = "Monthly donation"
            logger.info("Creating plan: {0}".format(name))
            stripe.Plan.create(
                id="monthly",
                amount=100,
                interval="month",
                interval_count=1,
                product={"name": name},
                currency="usd",
            )
        try:
            stripe.Plan.retrieve("quarterly")
            print("Quarterly plan exists, not creating!")
        except stripe.error.InvalidRequestError:
            name = "Quarterly donation"
            logger.info("Creating plan: {0}".format(name))
            stripe.Plan.create(
                id="quarterly",
                amount=100,
                interval="month",
                interval_count=3,
                nickname=name,
                product={"name": name},
                currency="usd",
            )
        try:
            stripe.Plan.retrieve("yearly")
            print("Yearly plan exists, not creating!")
        except stripe.error.InvalidRequestError:
            name = "Yearly donation"
            logger.info("Creating plan: {0}".format(name))
            stripe.Plan.create(
                id="yearly",
                amount=100,
                interval="year",
                interval_count=1,
                nickname=name,
                product={"name": name},
                currency="usd",
            )
