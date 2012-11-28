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
def spam_charfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.TextField)
def spam_textfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.DateTimeField)
def spam_datetimefield(model, field_type, field_name):
    pass


@super_global_handler(peewee.IntegerField)
def spam_floatfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.BooleanField)
def spam_floatfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.FloatField)
def spam_floatfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.DoubleField)
def spam_doublefield(model, field_type, field_name):
    pass


@super_global_handler(peewee.BigIntegerField)
def spam_bigintergerfield(model, field_type, field_name):
    #return random.randint(- 10 ** 10, 10 ** 10)
    pass


@super_global_handler(peewee.DecimalField)
def spam_decimalfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.PrimaryKeyField)
def spam_primarykeyfield(model, field_type, field_name):
    pass


@super_global_handler(peewee.ForeignKeyField)
def spam_datetimefield(model, field_type, field_name):
    pass


@super_global_handler(peewee.DateField)
def spam_datetimefield(model, field_type, field_name):
    pass


@super_global_handler(peewee.TimeField)
def spam_timefield(model, field_type, field_name):
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

    def spam_field(self, field, handler):
        pass

    def spam_model(self, model):
        """
        Iterates through all peewee attrs of a given model and gets the
        appropiate handler to spam each
        """

        attrs = {}  # this dict will hold all spammed attributes

        for field_name, field_instance in model._meta.get_sorted_fields():
            handler = self.get_handler(model, field_instance.__class__, field_name)
            if handler is not None:
                attr_value = handler(model, field_instance.__class__, field_name)
                attrs.update(field_name, attr_value)

        # create an instance of the model with the spammed fields and save it
        obj = model.create(**attrs)
        obj.save()

    def run(self):
        """Iterates through all models"""
        for model in self.__iter__():
            self.spam_model(model)