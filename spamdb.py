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


@super_global_handler('CharField')
def spam_charfield(field):
    pass


@super_global_handler('TextField')
def spam_textfield(field):
    pass


@super_global_handler('DateTimeField')
def spam_datetimefield(field):
    pass


@super_global_handler('IntegerField')
def spam_floatfield(field):
    pass


@super_global_handler('BooleanField')
def spam_floatfield(field):
    pass


@super_global_handler('FloatField')
def spam_floatfield(field):
    pass


@super_global_handler('DoubleField')
def spam_doublefield(field):
    pass


@super_global_handler('BigIntegerField')
def spam_bigintergerfield(field):
    #return random.randint(- 10 ** 10, 10 ** 10)
    pass


@super_global_handler('DecimalField')
def spam_decimalfield(field):
    pass


@super_global_handler('PrimaryKeyField')
def spam_primarykeyfield(field):
    pass


@super_global_handler('ForeignKeyField')
def spam_datetimefield(field):
    pass


@super_global_handler('DateField')
def spam_datetimefield(field):
    pass


@super_global_handler('TimeField')
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

    def append(self, item):

        if not issubclass(item, peewee.Model):
            raise TypeError, 'item is not of type peewee.Model'
        super(Spamdb, self).append(item)  # append the item to ourself (the list)

    def strict_handler(self, field_qname):
        """
        Used to override default behaviour for a custom field in a model
                Example usage:
                import spamdb
                import myapp.models


                sdb = spamdb.Spamdb()

                @sdb.strict_handler('models.User.name'):
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
                import myapp.models


                sdb = spamdb.Spamdb()

                @sdb.global_handler('CharField'):
                def spam_charfield(field):
                        # called when spamming all peewee.CharField fields
                    return "My custom string"
        """
        return _decorate(field_type, self.global_handlers)

    def spam(self, field_name, field_type):
        print field_name, field_type

    def run(self):
        """
        Iterates throw all models and their peewee attrs to
        spam them accordingly
        """
        for model in self.__iter__():
            for field_name, field_instance in model._meta.get_sorted_fields():
                self.spam(field_name, type(field_instance))