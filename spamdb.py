import peewee


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
def spam_charfield(field):
    pass


@super_global_handler(peewee.TextField)
def spam_textfield(field):
    pass


@super_global_handler(peewee.DateTimeField)
def spam_datetimefield(field):
    pass


@super_global_handler(peewee.IntegerField)
def spam_floatfield(field):
    pass


@super_global_handler(peewee.BooleanField)
def spam_floatfield(field):
    pass


@super_global_handler(peewee.FloatField)
def spam_floatfield(field):
    pass


@super_global_handler(peewee.DoubleField)
def spam_doublefield(field):
    pass


@super_global_handler(peewee.BigIntegerField)
def spam_bigintergerfield(field):
    #return random.randint(- 10 ** 10, 10 ** 10)
    pass


@super_global_handler(peewee.DecimalField)
def spam_decimalfield(field):
    pass


@super_global_handler(peewee.PrimaryKeyField)
def spam_primarykeyfield(field):
    pass


@super_global_handler(peewee.ForeignKeyField)
def spam_datetimefield(field):
    pass


@super_global_handler(peewee.DateField)
def spam_datetimefield(field):
    pass


@super_global_handler(peewee.TimeField)
def spam_timefield(field):
    pass


class Spamdb(list):

    def __init__(self, *args):
        # allow passing models as positional arguments
        # so it is possible to do s = Spamdb(model, another_model)
        for a in args:
            self.append(a)

        # used to register custom handler for fields
        self.global_handlers = SUPER_GLOBAL_HANDLERS
        self.strict_handlers = {}

    def strict_handler(self, field_qname):
        """
        Used to override default behaviour for a custom field in a model
                Example usage:
                import spamdb
                import myapp.models


                sdb = spamdb.Spamdb()

                @sdb.strict_handler(models.User.name):
                def spam_username(field):
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
                def spam_charfield(field):
                    # called when spamming all peewee.CharField fields
                    return "My custom string"
        """
        return _decorate(field_type, self.global_handlers)

    def get_handler(self, model, field):
        pass

    def spam_field(self, field, handler):
        pass

    def spam_model(self, model):
        """
        Iterates through all peewee attrs of a given model and gets the
        appropiate handler to spam each
        """

        attrs = {}  # this dict will hold all spammed attributes

        for field_name, field_instance in model._meta.get_sorted_fields():
            handler = self.get_handler(model, field_name)
            if handler is not None:
                attr_value = handler()
                attrs.update(field_name, attr_value)

        # create an instance of the model with the spammed fields and save it
        obj = model.create(**attrs)
        obj.save()

    def run(self):
        """Iterates through all models"""
        for model in self.__iter__():
            self.spam_model(model)