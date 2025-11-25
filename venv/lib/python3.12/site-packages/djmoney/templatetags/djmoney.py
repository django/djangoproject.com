from decimal import Decimal

from django import template
from django.template import TemplateSyntaxError

from ..money import Money
from ..utils import MONEY_CLASSES


register = template.Library()


class MoneyLocalizeNode(template.Node):
    def __repr__(self):
        return "<MoneyLocalizeNode %d %s>" % (self.money.amount, self.money.currency)

    def __init__(self, money=None, amount=None, currency=None, use_l10n=None, var_name=None):
        if money and (amount or currency):
            raise Exception('You can define either "money" or the "amount" and "currency".')

        self.money = money
        self.amount = amount
        self.currency = currency
        self.use_l10n = use_l10n
        self.var_name = var_name

    @classmethod
    def handle_token(cls, parser, token):

        tokens = token.contents.split()

        # default value
        var_name = None
        use_l10n = True

        # GET variable var_name
        if len(tokens) > 3:
            if tokens[-2] == "as":
                var_name = parser.compile_filter(tokens[-1])
                # remove the already used data
                tokens = tokens[0:-2]

        # GET variable use_l10n
        if tokens[-1].lower() in ("on", "off"):
            use_l10n = tokens[-1].lower() == "on"
            # remove the already used data
            tokens.pop(-1)

        # GET variable money
        if len(tokens) == 2:
            return cls(money=parser.compile_filter(tokens[1]), var_name=var_name, use_l10n=use_l10n)

        # GET variable amount and currency
        if len(tokens) == 3:
            return cls(
                amount=parser.compile_filter(tokens[1]),
                currency=parser.compile_filter(tokens[2]),
                var_name=var_name,
                use_l10n=use_l10n,
            )

        raise TemplateSyntaxError("Wrong number of input data to the tag.")

    def render(self, context):

        money = self.money.resolve(context) if self.money else None
        amount = self.amount.resolve(context) if self.amount else None
        currency = self.currency.resolve(context) if self.currency else None

        if money is not None:
            if not isinstance(money, MONEY_CLASSES):
                raise TemplateSyntaxError('The variable "money" must be an instance of Money.')

        elif amount is not None and currency is not None:
            money = Money(Decimal(str(amount)), str(currency))
        else:
            raise TemplateSyntaxError("You must define both variables: amount and currency.")

        money.use_l10n = self.use_l10n

        if self.var_name is None:
            return str(money)

        # as <var_name>
        context[self.var_name.token] = money
        return ""


@register.tag
def money_localize(parser, token):
    """
    Usage::

        {% money_localize <money_object> [ on(default) | off ] [as var_name] %}
        {% money_localize <amount> <currency> [ on(default) | off ] [as var_name] %}

    Example:

        The same effect:
        {% money_localize money_object %}
        {% money_localize money_object on %}

        Assignment to a variable:
        {% money_localize money_object on as NEW_MONEY_OBJECT %}

        Formatting the number with currency:
        {% money_localize '4.5' 'USD' %}

    Return::

        Money object

    """
    return MoneyLocalizeNode.handle_token(parser, token)
