from django.db import migrations


def populate_cvss_v4_fields(apps, schema_editor):
    SecurityIssue = apps.get_model("checklists", "SecurityIssue")
    for issue in SecurityIssue.objects.exclude(cvss_base_score=0):
        issue.cvss_v4_score = issue.cvss_base_score
        issue.cvss_v4_vector_string = "/".join(
            [
                "CVSS:4.0",
                f"AV:{issue.attack_vector}",
                f"AC:{issue.attack_complexity}",
                f"AT:{issue.attack_requirements}",
                f"PR:{issue.privileges_required}",
                f"UI:{issue.user_interaction}",
                f"VC:{issue.vuln_confidentiality_impact}",
                f"SC:{issue.sub_confidentiality_impact}",
                f"VI:{issue.vuln_integrity_impact}",
                f"SI:{issue.sub_integrity_impact}",
                f"VA:{issue.vuln_availability_impact}",
                f"SA:{issue.sub_availability_impact}",
            ]
        )
        issue.save()


class Migration(migrations.Migration):
    dependencies = [
        ("checklists", "0004_securityissue_cvss_v3_score_and_more"),
    ]

    operations = [
        migrations.RunPython(
            populate_cvss_v4_fields,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
