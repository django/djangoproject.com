from graphene.test import Client  # type: ignore

from django_countries.tests.graphql.schema import schema
from django_countries.tests.models import Person


def test_country_type(db):
    Person.objects.create(name="Skippy", country="AU")
    client = Client(schema)
    executed = client.execute("""{ people { name, country {name} } }""")
    returned_person = executed["data"]["people"][0]
    assert returned_person == {"name": "Skippy", "country": {"name": "Australia"}}
