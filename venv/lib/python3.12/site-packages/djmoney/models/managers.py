from functools import wraps

from django.core.exceptions import FieldDoesNotExist
from django.db.models import NOT_PROVIDED, Case, F, Q
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import BaseExpression
from django.db.models.functions import Cast, Coalesce
from django.utils.encoding import smart_str

from ..utils import MONEY_CLASSES, get_currency_field_name, prepare_expression
from .fields import CurrencyField, MoneyField


def _get_clean_name(model, name):
    # Get rid of __lt, __gt etc for the currency lookup
    if LOOKUP_SEP not in name:
        return name
    lookup_fields = name.split(LOOKUP_SEP)
    field = _get_field(model, name)
    return name.rsplit(LOOKUP_SEP, lookup_fields.index(field.name) + 1)[0]


def _get_field(model, name):
    lookup_fields = name.split(LOOKUP_SEP)
    prev_field = None
    opts = model._meta
    for field_name in lookup_fields:
        if field_name == "pk":
            field_name = opts.pk.name
        try:
            field = opts.get_field(field_name)
        except FieldDoesNotExist:
            # Ignore valid query lookups.
            if prev_field and prev_field.get_lookup(field_name):
                continue
        else:
            prev_field = field
            if hasattr(field, "get_path_info"):
                # This field is a relation, update opts to follow the relation
                path_info = field.get_path_info()
                opts = path_info[-1].to_opts
    return prev_field


def is_in_lookup(name, value):
    return hasattr(value, "__iter__") & (name.split(LOOKUP_SEP)[-1] == "in")


def _convert_in_lookup(model, field_name, options):
    """
    ``in`` lookup can not be represented as keyword lookup.
    It requires transformation to combination of ``Q`` objects.

    Example:

        amount__in=[Money(10, 'EUR'), Money(5, 'USD)]

        is equivalent to:

        Q(amount=10, amount_currency='EUR') or Q(amount=5, amount_currency='USD')
    """
    field = _get_field(model, field_name)
    new_query = Q()
    for value in options:
        if isinstance(value, MONEY_CLASSES):
            # amount__in=[Money(1, 'EUR'), Money(2, 'EUR')]
            option = {field.name: value.amount, get_currency_field_name(field.name, field): value.currency}
        elif isinstance(value, F):
            # amount__in=[Money(1, 'EUR'), F('another_money')]
            target_field = _get_field(model, value.name)
            option = {
                field.name: value,
                get_currency_field_name(field.name, field): F(get_currency_field_name(value.name, target_field)),
            }
        else:
            # amount__in=[1, 2, 3]
            option = {field.name: value}
        new_query |= Q(**option)
    return new_query


def _expand_money_args(model, args):
    """
    Augments args so that they contain _currency lookups - ie.. Q() | Q()
    """
    for arg in args:
        if isinstance(arg, Q):
            _expand_arg(model, arg)
    return args


def _expand_arg(model, arg):
    for i, child in enumerate(arg.children):
        if isinstance(child, Q):
            _expand_arg(model, child)
        elif isinstance(child, (list, tuple)):
            name, value = child
            field = _get_field(model, name)
            if isinstance(value, MONEY_CLASSES):
                clean_name = _get_clean_name(model, name)
                currency_field_name = get_currency_field_name(clean_name, field)
                arg.children[i] = Q(child, (currency_field_name, smart_str(value.currency)))
            if isinstance(field, MoneyField):
                if isinstance(value, (BaseExpression, F)):
                    clean_name = _get_clean_name(model, name)
                    if not isinstance(value, F):
                        value = prepare_expression(value)
                    if not _is_money_field(model, value, name):
                        continue
                    currency_field_name = get_currency_field_name(clean_name, field)
                    target_field = _get_field(model, value.name)
                    arg.children[i] = Q(
                        child, (currency_field_name, F(get_currency_field_name(value.name, target_field)))
                    )
                if is_in_lookup(name, value):
                    arg.children[i] = _convert_in_lookup(model, name, value)


def _is_money_field(model, rhs, lhs_name):
    """
    Checks if the target field from the expression is instance of MoneyField.
    """
    # If the right side is the same field, then no reason to check
    if rhs.name == lhs_name:
        return True
    target_field = _get_field(model, rhs.name)
    return isinstance(target_field, MoneyField)


def _expand_money_kwargs(model, args=(), kwargs=None, exclusions=()):
    """
    Augments kwargs so that they contain _currency lookups.
    """
    for name, value in list(kwargs.items()):
        if name in exclusions:
            continue
        field = _get_field(model, name)
        if isinstance(value, MONEY_CLASSES):
            clean_name = _get_clean_name(model, name)
            kwargs[name] = value.amount
            currency_field_name = get_currency_field_name(clean_name, field)
            kwargs[currency_field_name] = smart_str(value.currency)
        else:
            if isinstance(field, MoneyField):
                if isinstance(value, (BaseExpression, F)) and not isinstance(value, (Case, Cast, Coalesce)):
                    clean_name = _get_clean_name(model, name)
                    if not isinstance(value, F):
                        value = prepare_expression(value)
                    if not _is_money_field(model, value, name):
                        continue
                    currency_field_name = get_currency_field_name(clean_name, field)
                    target_field = _get_field(model, value.name)
                    kwargs[currency_field_name] = F(get_currency_field_name(value.name, target_field))
                if is_in_lookup(name, value):
                    args += (_convert_in_lookup(model, name, value),)
                    del kwargs[name]
            elif isinstance(field, CurrencyField) and "defaults" in exclusions:
                _handle_currency_field(model, name, kwargs)

    return args, kwargs


def _handle_currency_field(model, name, kwargs):
    name = _get_clean_name(model, name)
    field = _get_field(model, name)
    money_field = field.price_field
    if money_field.default is not NOT_PROVIDED and money_field.name not in kwargs:
        kwargs["defaults"] = kwargs.get("defaults", {})
        kwargs["defaults"][money_field.name] = money_field.default.amount


def _get_model(args, func):
    """
    Returns the model class for given function.
    Note, that ``self`` is not available for proxy models.
    """
    if hasattr(func, "__self__"):
        # Bound method
        model = func.__self__.model
    elif hasattr(func, "__wrapped__"):
        # Proxy model
        model = func.__wrapped__.__self__.model
    else:
        # Custom method on user-defined model manager.
        model = args[0].model
    return model


def understands_money(func):
    """
    Used to wrap a queryset method with logic to expand
    a query from something like:

    mymodel.objects.filter(money=Money(100, "USD"))

    To something equivalent to:

    mymodel.objects.filter(money=Decimal("100.0"), money_currency="USD")
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        model = _get_model(args, func)
        args = _expand_money_args(model, args)
        exclusions = EXPAND_EXCLUSIONS.get(func.__name__, ())
        args, kwargs = _expand_money_kwargs(model, args, kwargs, exclusions)
        queryset = func(*args, **kwargs)
        return add_money_comprehension_to_queryset(queryset)

    return wrapper


RELEVANT_QUERYSET_METHODS = ("distinct", "get", "get_or_create", "filter", "exclude", "update", "order_by")
EXPAND_EXCLUSIONS = {"get_or_create": ("defaults",)}


def add_money_comprehension_to_queryset(qs):
    # Decorate each relevant method with understands_money in the queryset given
    for attr in RELEVANT_QUERYSET_METHODS:
        method = getattr(qs, attr, None)
        if method is not None:
            setattr(qs, attr, understands_money(method))
    return qs


def money_manager(manager):
    """
    Patches a model manager's get_queryset method so that each QuerySet it returns
    is able to work on money fields.

    This allow users of django-money to use other managers while still doing
    money queries.
    """

    # Need to dynamically subclass to add our behaviour, and then change
    # the class of 'manager' to our subclass.

    # Rejected alternatives:
    #
    # * A monkey patch that adds things to the manager instance dictionary.
    #   This fails due to complications with Manager._copy_to_model behaviour.
    #
    # * Returning a new MoneyManager instance (rather than modifying
    #   the passed in manager instance). This fails for reasons that
    #   are tricky to get to the bottom of - Manager does funny things.
    class MoneyManager(manager.__class__):
        def get_queryset(self, *args, **kwargs):
            queryset = super().get_queryset(*args, **kwargs)
            return add_money_comprehension_to_queryset(queryset)

    manager.__class__ = MoneyManager
    return manager
