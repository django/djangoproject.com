import graphene  # type: ignore


class Country(graphene.ObjectType):
    name = graphene.String(description="Country name")
    code = graphene.String(description="ISO 3166-1 two character country code")
    alpha3 = graphene.String(description="ISO 3166-1 three character country code")
    numeric = graphene.Int(description="ISO 3166-1 numeric country code")
    ioc_code = graphene.String(
        description="International Olympic Committee country code"
    )

    @staticmethod
    def resolve_name(country, info):
        return country.name

    @staticmethod
    def resolve_code(country, info):
        return country.code

    @staticmethod
    def resolve_alpha3(country, info):
        return country.alpha3

    @staticmethod
    def resolve_numeric(country, info):
        return country.numeric

    @staticmethod
    def resolve_ioc_code(country, info):
        return country.ioc_code
