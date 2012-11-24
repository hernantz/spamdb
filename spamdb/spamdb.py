import peewee
import inspect


class Spamdb(list):

    # shortcut to append
    add = list.append

    def __init__(self, *args):
        # allow passing models as positional arguments
        # so it is possible to do s = Spamdb(model, another_model)
        for a in args:
            self.append(a)

        # used to register custom handler for fields and types
        self.global_handlers = {}
        self.strict_handlers = {}

    def _decorate(self, key, attr):
        def fn(f):
            attr.update({key: f})
            return f
        return fn

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
        return self._decorate(field_qname, self.strict_handlers)

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
        return self._decorate(field_type, self.global_handlers)

    def run(self):
        """
        Iterates throw all models and their peewee attrs to
        spam them accordingly
        """
        for model in self.__iter__():
            for k, v in inspect.getmembers(model):
                if type(v) == peewee.CharField:
                    print k, type(v)
                elif type(v) == peewee.DateTimeField:
                    print k, type(v)