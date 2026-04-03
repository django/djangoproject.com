# Release Checklists

The `checklists` app provides assistance for issuing Django releases (feature
releases, pre-releases (alpha/beta/RC), bugfix releases, and security releases).

## Key features

- **Release checklists**: Step-by-step markdown checklists for each release type
- **CVE tracking**: Full CVSS v4.0 support for security vulnerabilities
- **Blogpost generation**: Automated ReStructuredText blogpost templates
- **Release coordination**: Track multiple releases affected by security issues

## URLs

- `/checklists/release/<version>/` - Public release checklist (e.g., `/checklists/release/5.2/`)
- `/checklists/security/release/<pk>/` - Security release checklist (login + permissions required)
- `/checklists/security/issue/<cve_id>/` - CVE JSON record (login + permissions required)

## Required permissions for security views

- `checklists.view_securityrelease` - View security release checklists
- `checklists.view_securityissue` - View CVE details and JSON records

## Setup for release managers

1. Create a `Releaser` object in the admin linking to the user's account with GPG key info
2. Assign the security permissions to users who need access to pre-disclosure CVE information

## Models

- `Releaser` - Release managers
- `FeatureRelease` - Major/minor releases (X.Y.0)
- `PreRelease` - Alpha, beta, and RC releases
- `BugFixRelease` - Patch releases (X.Y.Z)
- `SecurityRelease` - Coordinated security releases
- `SecurityIssue` - CVE tracking with CVSS v4.0 metrics
- `SecurityIssueReleasesThrough` - Links CVEs to affected Django versions
