"""Request reviews from the teams in CODEOWNERS that own files changed by a PR.

Usage: request-codeowner-reviews.py [--dry-run] PR_NUMBER

Reads GITHUB_REPOSITORY ("org/repo") and, optionally, GITHUB_TOKEN from the
environment. CODEOWNERS is read from the repository's default branch.
"""

import argparse
import json
import os
import sys
from fnmatch import fnmatch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = os.environ["GITHUB_REPOSITORY"]
ORG = REPO.split("/")[0]


def github(path, data=None, accept="application/vnd.github+json"):
    headers = {"Accept": accept}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        f"https://api.github.com/repos/{REPO}/{path}",
        data=json.dumps(data).encode() if data else None,
        headers=headers,
    )
    try:
        with urlopen(request) as response:
            body = response.read()
    except HTTPError as error:
        sys.exit(f"{error}: {error.read().decode()}")
    return body.decode() if accept.endswith(".raw") else json.loads(body)


def changed_files(pr):
    files = []
    page = 1
    while batch := github(f"pulls/{pr}/files?per_page=100&page={page}"):
        files += [f["filename"] for f in batch]
        page += 1
    return files


def owning_teams(codeowners, files):
    teams = set()
    for line in codeowners.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        pattern, *owners = line.split()
        # "dir/**/*" -> "dir/*" (fnmatch's * also matches "/")
        pattern = pattern.replace("/**/", "/")
        if any(fnmatch(f, pattern) for f in files):
            teams.update(
                owner.removeprefix(f"@{ORG}/")
                for owner in owners
                if owner.startswith(f"@{ORG}/")
            )
    return sorted(teams)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pr", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    codeowners = github(
        "contents/.github/CODEOWNERS", accept="application/vnd.github.raw"
    )
    teams = owning_teams(codeowners, changed_files(args.pr))

    print(f"Requesting reviews from: {', '.join(teams) or 'nobody'}")
    if teams and not args.dry_run:
        github(f"pulls/{args.pr}/requested_reviewers", data={"team_reviewers": teams})


if __name__ == "__main__":
    main()
