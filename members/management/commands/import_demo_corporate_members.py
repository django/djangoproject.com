"""
Populate the local database with the corporate members listed on the live
djangoproject.com site, including their logos, so the homepage sponsor grid
can be previewed with real data.

This is a development/demo helper. It requires network access.

Usage::

    python -m manage import_demo_corporate_members
    python -m manage import_demo_corporate_members --force
"""

import datetime
import html
import os
import re
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from ...models import (
    BRONZE_MEMBERSHIP,
    DIAMOND_MEMBERSHIP,
    GOLD_MEMBERSHIP,
    PLATINUM_MEMBERSHIP,
    SILVER_MEMBERSHIP,
    SPONSORED_FELLOW_MEMBERSHIP,
    CorporateMember,
    Invoice,
)

DEFAULT_SOURCE = "https://www.djangoproject.com/foundation/corporate-members/"
USER_AGENT = "Mozilla/5.0 (djangoproject.com demo importer)"

TIERS = (
    ("sponsored fellow", SPONSORED_FELLOW_MEMBERSHIP),
    ("diamond", DIAMOND_MEMBERSHIP),
    ("platinum", PLATINUM_MEMBERSHIP),
    ("gold", GOLD_MEMBERSHIP),
    ("silver", SILVER_MEMBERSHIP),
    ("bronze", BRONZE_MEMBERSHIP),
)

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
TIER_RE = re.compile(
    r"<h3>\s*([^<]*Corporate Members[^<]*)</h3>\s*"
    r'<ul[^>]*class="corporate-members"[^>]*>(.*?)</ul>',
    re.DOTALL,
)
LI_RE = re.compile(r"<li\b[^>]*>(.*?)</li>", re.DOTALL)
IMG_RE = re.compile(r"<img\b[^>]*>", re.DOTALL)
LINK_RE = re.compile(r'<h3>\s*<a\s+href="([^"]+)"[^>]*>(.*?)</a>\s*</h3>', re.DOTALL)
DESC_RE = re.compile(r"<p>(.*?)</p>", re.DOTALL)
ATTR_RE = {
    "src": re.compile(r'\bsrc="([^"]+)"'),
    "alt": re.compile(r'\balt="([^"]+)"'),
}


def clean_text(text):
    return WHITESPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", text))).strip()


class Command(BaseCommand):
    help = "Import demo corporate members (and logos) from the live site."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=DEFAULT_SOURCE,
            help="URL of the corporate members page to import from.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-download logos even for members that already have one.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        force = options["force"]

        self.stdout.write(f"Fetching {source} ...")
        try:
            response = requests.get(
                source, headers={"User-Agent": USER_AGENT}, timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CommandError(f"Could not fetch {source}: {exc}") from exc

        members = self.parse(response.text)
        if not members:
            raise CommandError("No corporate members were found in the response.")

        created = updated = logos = 0
        for entry in members:
            member, was_created = CorporateMember.objects.update_or_create(
                display_name=entry["name"],
                defaults={
                    "url": entry["url"],
                    "description": entry["description"],
                    "contact_name": entry["name"],
                    "contact_email": "demo@example.com",
                    "membership_level": entry["level"],
                },
            )
            created += was_created
            updated += not was_created

            if entry["logo"] and (force or not member.logo):
                if self.download_logo(member, entry["logo"]):
                    logos += 1

            self.ensure_invoice(member)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(members)} members "
                f"({created} created, {updated} updated, {logos} logos)."
            )
        )

    def parse(self, page):
        entries = []
        for heading, body in TIER_RE.findall(page):
            level = self.tier_level(heading)
            if level is None:
                continue
            for item in LI_RE.findall(body):
                entry = self.parse_member(item, level)
                if entry:
                    entries.append(entry)
        return entries

    def tier_level(self, heading):
        lowered = heading.lower()
        for name, level in TIERS:
            if name in lowered:
                return level
        return None

    def parse_member(self, item, level):
        link = LINK_RE.search(item)
        img = IMG_RE.search(item)
        alt = ""
        logo = ""
        if img:
            src_match = ATTR_RE["src"].search(img.group(0))
            alt_match = ATTR_RE["alt"].search(img.group(0))
            logo = src_match.group(1) if src_match else ""
            alt = alt_match.group(1) if alt_match else ""

        name = clean_text(link.group(2)) if link else clean_text(alt)
        if not name:
            return None

        desc = DESC_RE.search(item)
        return {
            "name": name,
            "url": link.group(1) if link else "",
            "description": clean_text(desc.group(1)) if desc else "",
            "logo": logo,
            "level": level,
        }

    def download_logo(self, member, url):
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.stderr.write(f"  ! Could not download logo for {member}: {exc}")
            return False

        filename = os.path.basename(urlparse(url).path) or f"{member.pk}.png"
        member.logo.save(filename, ContentFile(response.content), save=True)
        return True

    def ensure_invoice(self, member):
        if member.invoice_set.exists():
            return
        Invoice.objects.create(
            member=member,
            amount=1,
            expiration_date=datetime.date(2030, 12, 31),
        )
