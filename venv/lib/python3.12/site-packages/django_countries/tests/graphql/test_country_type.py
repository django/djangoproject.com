from graphene.test import Client  # type: ignore

from django_countries.tests.graphql.schema import schema


def test_country_type():
    client = Client(schema)
    executed = client.execute(
        """{ newZealand {code, name, iocCode, numeric, alpha3} }"""
    )
    returned_country = executed["data"]["newZealand"]
    assert returned_country == {
        "code": "NZ",
        "name": "New Zealand",
        "iocCode": "NZL",
        "numeric": 554,
        "alpha3": "NZL",
    }
