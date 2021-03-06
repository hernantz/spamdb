import peewee
import datetime
import decimal
import lorem_ipsum
import random

__all__ = ['SUPER_GLOBAL_HANDLERS', 'super_global_handler', '_decorate',
           'Spamdb', 'spam_charfield', 'spam_textfield', 'spam_datetimefield',
           'spam_floatfield', 'spam_doublefield', 'spam_bigintegerfield',
           'spam_decimalfield', 'spam_primarykeyfield', 'spam_timefield',
           'spam_integerfield', 'spam_booleanfield', 'spam_datefield',
           'spam_foreignkeyfield', 'spam_choices']

SUPER_GLOBAL_HANDLERS = {}  # will hold all spam functions for every field type


def super_global_handler(field_name):
    return _decorate(field_name, SUPER_GLOBAL_HANDLERS)


def _decorate(key, container):
    """
    Decorator user to register function handlers on a given
    container
    """
    def fn(f):
        container.update({key: f})
        return f
    return fn


@super_global_handler(peewee.CharField)
def spam_charfield(model, field_type, field_name):
    """
    Returns a random lorem ipsum sentence that does not overpass the
    field's max_length attribute
    """
    max_length = getattr(model, field_name).attributes['max_length']
    words = lorem_ipsum.sentence()
    if max_length < len(words):
        return words[:max_length].strip()
    return words


@super_global_handler(peewee.TextField)
def spam_textfield(model, field_type, field_name):
    """
    Return a random number between 1 and 10 of lorem ipsum paragraphs
    """
    return '.\n\n'.join(lorem_ipsum.paragraphs(random.randrange(1, 10)))


@super_global_handler(peewee.DateTimeField)
def spam_datetimefield(model, field_type, field_name):
    """
    Return a random date between now and two months ago.
    Consider days and time.
    """
    minutes = random.randint(0, 86400)  # 2 months ~= 60d ~= 1440h ~= 86400min
    return datetime.datetime.now() - datetime.timedelta(minutes=minutes)


@super_global_handler(peewee.IntegerField)
def spam_integerfield(model, field_type, field_name):
    return random.randint(-10000, 10000)


@super_global_handler(peewee.BooleanField)
def spam_booleanfield(model, field_type, field_name):
    return bool(random.randint(0, 1))


@super_global_handler(peewee.FloatField)
def spam_floatfield(model, field_type, field_name):
    num1 = float(random.randint(-10000, 10000))
    num2 = random.randint(1, 10000)
    return num1 / num2


@super_global_handler(peewee.DoubleField)
def spam_doublefield(model, field_type, field_name):
    return spam_floatfield(model, field_type, field_name)


@super_global_handler(peewee.BigIntegerField)
def spam_bigintegerfield(model, field_type, field_name):
    """
    Return a random int between +-10 million
    """
    return random.randint(-10000000000, 10000000000)  # 10 ** 10 = 10 million


@super_global_handler(peewee.DecimalField)
def spam_decimalfield(model, field_type, field_name):
    return decimal.Decimal(random.random() + random.randint(-10000, 10000))


@super_global_handler(peewee.PrimaryKeyField)
def spam_primarykeyfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.ForeignKeyField)
def spam_foreignkeyfield(model, field_type, field_name):
    related_model = getattr(model, field_name).rel_model
    query = related_model.select().order_by(peewee.fn.Random()).limit(1)
    if query.count():
        return [model for model in query][0]


@super_global_handler(peewee.DateField)
def spam_datefield(model, field_type, field_name):
    """
    Return a random date between now and two months ago.
    Consider days only.
    """
    random_days = random.randrange(0, 60)
    return datetime.date.today() - datetime.timedelta(days=random_days)


@super_global_handler(peewee.TimeField)
def spam_timefield(model, field_type, field_name):
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime.time(hour=hour, minute=minute, second=second)


def spam_choices(model, field_type, field_name):
    choices = getattr(model, field_name).choices
    return random.choice(choices)


def _coin_toss():
    """
    Used to ignore or not a nullable field
    """
    return bool(random.randint(0, 1))


class Spamdb(list):

    def __init__(self, *args):
        # allow passing models as positional arguments
        # so it is possible to do s = Spamdb(model, another_model)
        for a in args:
            self.append(a)

        # used to register custom handler for fields
        self.global_handlers = dict(SUPER_GLOBAL_HANDLERS)
        self.strict_handlers = {}

    def strict_handler(self, field_qname):
        """
        Used to override default behaviour for a custom field in a model
                Example usage:
                import spamdb
                import myapp.models


                sdb = spamdb.Spamdb()

                @sdb.strict_handler(models.User.name):
                def spam_username(model, field_type, field_name):
                    # called when spamming User.name field
                    return "Hi there!!"
        """
        return _decorate(field_qname, self.strict_handlers)

    def global_handler(self, field_type):
        """
        Used to override default behaviour for a field type in all models
                Example usage:
                import spamdb
                import peewee
                import myapp.models


                sdb = spamdb.Spamdb()

                @sdb.global_handler(peewee.CharField):
                def spam_charfield(model, field_type, field_name):
                    # called when spamming all peewee.CharField fields
                    return "My custom string"
        """
        return _decorate(field_type, self.global_handlers)

    def get_handler(self, model, field_type, field_name):
        """
        Lookup into the strict_handlers first and global_handlers later
        for a function mapped to a given model and field_name /  field_type
        """
        key = getattr(model, field_name, None)

        handler = self.strict_handlers.get(key, None)

        if not handler:
            handler = self.global_handlers.get(field_type, None)

        return handler

    def spam_fields(self, model):
        """
        Iterates through all peewee attrs of a given model and gets the
        appropiate handler to spam each.
        Returns a dict of model attributes as keys and the respective spammed
        content as values.
        """

        attrs = {}  # this dict will hold all spammed attributes

        for field_name, field_instance in model._meta.get_sorted_fields():
            params = (model, field_instance.__class__, field_name)

            if field_instance.null and _coin_toss():
                continue  # the field can be null and it was randomly skipped
            else:
                # otherwise the field can not be null
                # or can be null but was randomly set to have a value

                if field_instance.choices:
                    handler = spam_choices  # pick a random choice if possible
                else:
                    # find an appropiate handler
                    handler = self.get_handler(*params)

                attr_value = handler(*params)
                attrs.update({field_name: attr_value})

        return attrs

    def spam_model(self, model, save=False):
        """
        Creates and returns a spammed model.
        If save is True, it will persist the spammed object
        before returning it.
        """
        attributes = self.spam_fields(model)  # get spammed fields
        obj = model(**attributes)
        if save:
            obj.save()
        return obj

    def run(self, iterations=1):
        """Iterates through all models"""
        for i in range(0, iterations):
            for model in self.__iter__():
                self.spam_model(model, save=True)
