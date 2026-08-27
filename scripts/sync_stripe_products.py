"""
Sync Stripe products from the live account to the sandbox (test) account.
This script can be run only by the Ops Team who have permissions to the
Stripe live account and account-wide secret key for the sandbox account.

Uses (set in ``.envrc``, never committed):
    STRIPE_LIVE_PRODUCT_KEY    - restricted key for the live account. Must have
                                 the "Products Read" and "Prices Read"
                                 permissions enabled on the key.
    STRIPE_SANDBOX_SECRET_KEY  - the sandbox (test account) secret key
                                 (sk_test_...), from the sandbox dashboard
                                 (top-right switcher set to "Test mode" ->
                                 Developers -> API keys). Keep it
                                 separate from the site's public
                                 development key (see
                                 ``djangoproject/settings/common.py``) so
                                 the public cannot tamper with the shared
                                 sandbox products.

For each product listed in ``SITE_KEY_NAMES`` below, the product is
created in the sandbox if it doesn't exist (along with its fixed-amount
active prices) or updated if it has drifted from live. This script only
creates and updates: it never deletes or deactivates anything in the
sandbox, and products that aren't listed are left alone in both
accounts. To add or drop a site product, add a mapping in
``SITE_KEY_NAMES`` and re-run (the script refuses to run on a key the
settings ``PRODUCTS`` dict has no mapping for).

The sandbox ID of each listed product is written to
``djangoproject/settings/stripe_sandbox_product_ids.json`` after each sync,
so it can be checked in as the local development fallback.

Usage (from the project root, with direnv loading ``.envrc``):

    python scripts/sync_stripe_products.py --dry-run   # preview changes
    python scripts/sync_stripe_products.py             # apply changes
"""

import argparse
import json
import os
import sys

import stripe

# Committed file holding the sandbox product IDs used by the site.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
PRODUCT_IDS_FILE = os.path.join(
    BASE_DIR, "djangoproject", "settings", "stripe_sandbox_product_ids.json"
)

# Mapping used only when syncing: key in the settings ``PRODUCTS`` dict
# -> product name in the live Stripe account. The site itself never uses
# product names; they only identify which live product each key refers to.
SITE_KEY_NAMES = {
    "monthly": "Monthly donation",
    "quarterly": "Quarterly donation",
    "yearly": "Yearly donation",
    "onetime": "One-time Donation",
}

from djangoproject.settings.common import PRODUCTS  # noqa: E402


def validate_product_keys():
    """Exit if settings PRODUCTS has a key with no mapping here."""
    missing = set(PRODUCTS) - set(SITE_KEY_NAMES)
    if missing:
        sys.exit(
            "Error: the settings PRODUCTS dict has keys that are not in "
            f"SITE_KEY_NAMES in this script: {sorted(missing)}. Add a "
            "mapping (key -> live product name) before running."
        )


# Product fields mirrored from live to sandbox.
SYNCED_FIELDS = (
    "name",
    "description",
    "active",
    "metadata",
    "statements_descriptor",
    "unit_label",
)


def get_env(key):
    """The value of an environment variable, exiting if unset."""
    value = os.environ.get(key)
    if not value:
        sys.exit(f"Error: environment variable {key} is not set.")
    return value


def list_products(api_key):
    """All products in the given account."""
    products = []
    starting_after = None
    while True:
        params = {"limit": 100}
        if starting_after:
            params["starting_after"] = starting_after
        listing = stripe.Product.list(api_key=api_key, **params)
        products.extend(listing["data"])
        if not listing["has_more"]:
            break
        starting_after = listing["data"][-1]["id"]
    return products


def list_prices(api_key, product_id):
    """The active prices of a product."""
    prices = []
    starting_after = None
    while True:
        params = {"product": product_id, "active": True, "limit": 100}
        if starting_after:
            params["starting_after"] = starting_after
        listing = stripe.Price.list(api_key=api_key, **params)
        prices.extend(listing["data"])
        if not listing["has_more"]:
            break
        starting_after = listing["data"][-1]["id"]
    return prices


def price_identity(price):
    """Match key between a live price and its sandbox copy."""
    recurring = price.get("recurring")
    return (
        price["unit_amount"],
        price["currency"].lower(),
        recurring["interval"] if recurring else None,
        recurring["interval_count"] if recurring else None,
    )


def describe_price(price):
    """One-line summary of a price for reports."""
    recurring = price.get("recurring")
    if recurring:
        cadence = f"recurring {recurring['interval']} x{recurring['interval_count']}"
    else:
        cadence = "one-time"
    name = price.get("nickname") or price["id"]
    return f"{name} - {price['unit_amount']} {price['currency'].upper()} ({cadence})"


def write_product_ids(product_ids):
    """Write the IDs file if it changed; whether it did."""
    if os.path.exists(PRODUCT_IDS_FILE):
        with open(PRODUCT_IDS_FILE) as f:
            if json.load(f) == product_ids:
                return False
    with open(PRODUCT_IDS_FILE, "w") as f:
        json.dump(product_ids, f, indent=2, sort_keys=True)
        f.write("\n")
    return True


def fixed_prices(api_key, product_id):
    """The product's prices with a fixed amount (donor-entered excluded)."""
    return [p for p in list_prices(api_key, product_id) if p["unit_amount"] is not None]


def find_drift(live_product, sandbox_product, live_prices, sandbox_key):
    """Changed synced fields and missing prices of a sandbox product."""
    changed = [
        field
        for field in SYNCED_FIELDS
        if live_product.get(field) != sandbox_product.get(field)
    ]
    have = {price_identity(p) for p in list_prices(sandbox_key, sandbox_product["id"])}
    missing_prices = [p for p in live_prices if price_identity(p) not in have]
    return changed, missing_prices


def collect_actions(live_by_name, sandbox_by_name, live_key, sandbox_key):
    """The changes each site product needs: (actions, product_ids)."""
    actions = []
    product_ids = {key: "" for key in SITE_KEY_NAMES}
    for key, name in SITE_KEY_NAMES.items():
        live_product = live_by_name.get(name)
        if live_product is None:
            print(
                f"warning:   live product {name!r} (key {key!r}) not found, skipping."
            )
            continue

        prices = fixed_prices(live_key, live_product["id"])

        sandbox_product = sandbox_by_name.get(name)
        if sandbox_product is None:
            actions.append(("create", key, live_product, None, [], prices))
            continue

        product_ids[key] = sandbox_product["id"]
        changed, missing_prices = find_drift(
            live_product, sandbox_product, prices, sandbox_key
        )
        if not changed and not missing_prices:
            print(f"unchanged  {key} ({name!r})")
            continue
        actions.append(
            (
                "update",
                key,
                live_product,
                sandbox_product["id"],
                changed,
                missing_prices,
            )
        )
    return actions, product_ids


def report(actions, product_ids):
    """The planned changes, printed; the change count."""
    print()
    total = 0
    for kind, key, live_product, sandbox_id, changed, prices in actions:
        if kind == "create":
            print(f"create     {key}  {live_product['name']!r}")
        else:
            fields = ", ".join(changed) if changed else "no field changes"
            print(f"update     {key} -> {sandbox_id}  ({fields})")
        total += 1 + len(prices)
        for price in prices:
            print(f"price+     {key}  {describe_price(price)}")
    for key in SITE_KEY_NAMES:
        print(f"product ids  {key} = {product_ids[key]!r}")
    return total


def product_params(live_product, fields):
    """Stripe params for the given fields, excluding values that are None."""
    return {
        field: live_product[field]
        for field in fields
        if live_product.get(field) is not None
    }


def price_params(price, sandbox_id):
    """Stripe params for replicating the live price."""
    params = {
        "product": sandbox_id,
        "unit_amount": price["unit_amount"],
        "currency": price["currency"],
    }
    if price.get("nickname"):
        params["nickname"] = price["nickname"]
    if price.get("recurring"):
        params["recurring"] = {
            "interval": price["recurring"]["interval"],
            "interval_count": price["recurring"]["interval_count"],
        }
    return params


def apply(actions, product_ids, sandbox_key):
    """Apply the planned changes to the sandbox."""
    created = updated = prices_created = 0
    for kind, key, live_product, sandbox_id, changed, prices in actions:
        if kind == "create":
            params = product_params(live_product, SYNCED_FIELDS)
            product = stripe.Product.create(api_key=sandbox_key, **params)
            sandbox_id = product["id"]
            product_ids[key] = sandbox_id
            created += 1
            print(f"  created   {live_product['name']!r} as {sandbox_id}")
        else:
            params = product_params(live_product, changed)
            if params:
                stripe.Product.modify(api_key=sandbox_key, id=sandbox_id, **params)
                updated += 1
                print(f"  updated   {sandbox_id}")
        for price in prices:
            price_obj = stripe.Price.create(
                api_key=sandbox_key,
                **price_params(price, sandbox_id),
            )
            prices_created += 1
            print(
                f"  price+    {sandbox_id}  {describe_price(price)} "
                f"as {price_obj['id']}"
            )
    return created, updated, prices_created


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show the changes that would be made, don't apply them.",
    )
    args = parser.parse_args()

    validate_product_keys()

    live_key = get_env("STRIPE_LIVE_PRODUCT_KEY")
    sandbox_key = get_env("STRIPE_SANDBOX_SECRET_KEY")

    actions, product_ids = collect_actions(
        {p["name"]: p for p in list_products(live_key)},
        {p["name"]: p for p in list_products(sandbox_key)},
        live_key,
        sandbox_key,
    )

    # --- Report ----------------------------------------------------------------
    total = report(actions, product_ids)
    if not total:
        print("\nSandbox already matches the listed products and prices.")
        # Keep the IDs file in sync even when nothing changed.
        if write_product_ids(product_ids):
            print(f"Updated {os.path.relpath(PRODUCT_IDS_FILE, BASE_DIR)}")
        return

    if args.dry_run:
        print(
            f"\nDry run: {total} change(s) would be made; "
            f"{os.path.relpath(PRODUCT_IDS_FILE, BASE_DIR)} would be "
            f"rewritten with the new sandbox IDs. "
            f"Re-run without --dry-run to apply."
        )
        return

    # --- Apply -----------------------------------------------------------------
    created, updated, prices_created = apply(actions, product_ids, sandbox_key)
    if write_product_ids(product_ids):
        print(f"Updated {os.path.relpath(PRODUCT_IDS_FILE, BASE_DIR)}")

    print(
        f"\nDone: {created} created, {updated} updated, "
        f"{prices_created} price(s) created."
    )


if __name__ == "__main__":
    stripe_version = "2020-08-27"  # matches the version pinned in the site
    stripe.api_version = stripe_version
    main()
