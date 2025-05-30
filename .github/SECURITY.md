# Security Policies and Procedures

This document outlines security procedures and general policies for the Django website (`djangoproject.com`). This is separate from [Django's security policies](https://docs.djangoproject.com/en/dev/internals/security/).

  * [Reporting a Bug](#reporting-a-bug)
  * [Reporting Guidelines](#reporting-guidelines)
  * [Disclosure Policy](#disclosure-policy)
  * [Comments on this Policy](#comments-on-this-policy)

## Reporting a Bug

The Django website working group is committed to responsible reporting and
disclosure of security-related issue in our website. We appreciate your efforts
and responsible disclosure.

Report security bugs and issue by sending an email to website-wg@djangoproject.com.
For encryption, use: https://keys.openpgp.org/vks/v1/by-fingerprint/AF3516D27D0621171E0CCE25FCB84B8D1D17F80B

Once you’ve submitted an issue via email, you should receive an acknowledgment
from a member of the website working group within 3 working days. After that,
the website working group will begin their analysis. Depending on the action
to be taken, you may receive followup emails. It can take several weeks before
the website working group comes to a conclusion and resolve the issue.

## Reporting Guidelines

While reporting a security issue related to the Django website, we encourage
to follow few guidelines that helps us in analysis and resolving the issue quicker.

  * Include a runnable proof of concept to reproduce the issue
  * User input must be sanitized

## Disclosure Policy

When the website working group receives a security bug report, they will
identify and fix the issues in the website, involving the following steps:

  * Confirm the problem.
  * Audit code to find any potential similar problems.
  * Apply the relevant patches to the codebase.
  * Deploy the fixed codebase.

## Comments on this Policy

If you have suggestions on how this process could be improved please submit a
pull request.
