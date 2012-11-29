import unittest
import datetime
from spamdb import *
from spamdb import _decorate
from peewee import *


class TestModel(Model):
    """
    Base test model class
    """
    class Meta:
        database = '/tmp/test.db'


# Model classes used by test cases


class User(TestModel):
    username = CharField()

    class Meta:
        db_table = 'users'


class Blog(TestModel):
    user = ForeignKeyField(User)
    title = CharField(max_length=25)
    content = TextField(default='')
    pub_date = DateTimeField(null=True)
    pk = PrimaryKeyField()

    def __unicode__(self):
        return '%s: %s' % (self.user.username, self.title)


class Comment(TestModel):
    blog = ForeignKeyField(Blog, related_name='comments')
    comment = CharField()


class Relationship(TestModel):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')


class NullModel(TestModel):
    char_field = CharField(null=True)
    text_field = TextField(null=True)
    datetime_field = DateTimeField(null=True)
    int_field = IntegerField(null=True)
    float_field = FloatField(null=True)
    decimal_field1 = DecimalField(null=True)
    decimal_field2 = DecimalField(decimal_places=2, null=True)
    double_field = DoubleField(null=True)
    bigint_field = BigIntegerField(null=True)
    date_field = DateField(null=True)
    time_field = TimeField(null=True)
    boolean_field = BooleanField(null=True)


class UniqueModel(TestModel):
    name = CharField(unique=True)


class OrderedModel(TestModel):
    title = CharField()
    created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-created',)


class Category(TestModel):
    parent = ForeignKeyField('self', related_name='children', null=True)
    name = CharField()


class UserCategory(TestModel):
    user = ForeignKeyField(User)
    category = ForeignKeyField(Category)


class NonIntModel(TestModel):
    pk = CharField(primary_key=True)
    data = CharField()


class NonIntRelModel(TestModel):
    non_int_model = ForeignKeyField(NonIntModel, related_name='nr')


class DBUser(TestModel):
    user_id = PrimaryKeyField(db_column='db_user_id')
    username = CharField(db_column='db_username')


class DBBlog(TestModel):
    blog_id = PrimaryKeyField(db_column='db_blog_id')
    title = CharField(db_column='db_title')
    user = ForeignKeyField(DBUser, db_column='db_user')


class SeqModelA(TestModel):
    id = IntegerField(primary_key=True, sequence='just_testing_seq')
    num = IntegerField()


class SeqModelB(TestModel):
    id = IntegerField(primary_key=True, sequence='just_testing_seq')
    other_num = IntegerField()


class MultiIndexModel(TestModel):
    f1 = CharField()
    f2 = CharField()
    f3 = CharField()

    class Meta:
        indexes = (
            (('f1', 'f2'), True),
            (('f2', 'f3'), False),
        )


class BlogTwo(Blog):
    title = TextField()
    extra_field = CharField()


class Parent(TestModel):
    data = CharField()


class Child(TestModel):
    parent = ForeignKeyField(Parent)


class Orphan(TestModel):
    parent = ForeignKeyField(Parent, null=True)


class ChildPet(TestModel):
    child = ForeignKeyField(Child)


class OrphanPet(TestModel):
    orphan = ForeignKeyField(Orphan)


MODELS = [User, Blog, Comment, Relationship, NullModel, UniqueModel, OrderedModel, Category, UserCategory,
          NonIntModel, NonIntRelModel, DBUser, DBBlog, SeqModelA, SeqModelB, MultiIndexModel, BlogTwo]


def drop_tables(only=None):
    for model in reversed(MODELS):
        if only is None or model in only:
            model.drop_table(True)


def create_tables(only=None):
    for model in MODELS:
        if only is None or model in only:
            model.create_table()


class ModelTestCase(unittest.TestCase):
    requires = None

    def setUp(self):
        drop_tables(self.requires)
        create_tables(self.requires)

    def tearDown(self):
        drop_tables(self.requires)

    def create_user(self, username):
        return User.create(username=username)

    def create_users(self, n):
        for i in range(n):
            self.create_user('u%d' % (i + 1))


class AddModelTestCase(unittest.TestCase):
    """Test that Spamdb contains the right models"""

    def test_add_model(self):
        """
        A Spamdb instance should contain the models passed as params,
        and in the order they where added
        """
        sdb = Spamdb(User, Blog)
        sdb.append(Comment)
        self.assertEquals(sdb[0], User)
        self.assertEquals(sdb[1], Blog)
        self.assertEquals(sdb[2], Comment)


class HandlerDecoratorsTestCase(unittest.TestCase):
    """
    Test that the _decorate function registers the decorated function
    in the given container
    """

    def test_handler_decorator(self):
        """
        The _decorate function should register the decorated function
        in the given container
        """
        container = {}
        key = 'test'

        def empty_function():
            pass

        decorator = _decorate(key, container)
        decorator(empty_function)()

        self.assertEquals({'test': empty_function}, container)

    def test_super_global_handlers_mapping(self):
        """
        The super_global_handler decorator should add
        the decorated function into the global_handlers dict in a Spamdb obj
        """
        @super_global_handler(User)
        def empty_function():
            pass

        self.assertTrue(User in SUPER_GLOBAL_HANDLERS)
        self.assertTrue(User in Spamdb().global_handlers)
        self.assertFalse(User in Spamdb().strict_handlers)

        del SUPER_GLOBAL_HANDLERS[User]  # don't polute other tests

    def test_global_handlers_mapping(self):
        """
        The global_handler decorator should add
        the decorated function into the global_handlers dict in a Spamdb obj
        """

        sdb = Spamdb()

        @sdb.global_handler(User)
        def empty_function():
            pass

        self.assertTrue(User in sdb.global_handlers)
        self.assertFalse(User in sdb.strict_handlers)

        del SUPER_GLOBAL_HANDLERS[User]  # don't polute other tests

    def test_strict_handlers_mapping(self):
        """
        The strict_handler decorator should add
        the decorated function into the strict_handlers dict in a Spamdb obj
        """

        sdb = Spamdb()

        @sdb.strict_handler(User)
        def empty_function():
            pass

        self.assertTrue(User in sdb.strict_handlers)
        self.assertFalse(User in sdb.global_handlers)

    def test_get_global_handler(self):
        """
        The Spamdb.get_handler method should return a
        globally registered spam function
        """

        sdb = Spamdb()

        @sdb.global_handler(CharField)
        def empty_function():
            pass

        handler = sdb.get_handler(User, User.username.__class__, 'username')
        self.assertEquals(handler, empty_function)

    def test_get_strict_handler(self):
        """
        The Spamdb.get_handler method should return a
        strictly registered spam function
        """

        sdb = Spamdb()

        @sdb.global_handler(CharField)
        def empty_global_function():
            pass

        @sdb.strict_handler(User.username)
        def empty_strict_function():
            pass

        handler = sdb.get_handler(User, User.username.__class__, 'username')
        self.assertEquals(handler, empty_strict_function)
        self.assertTrue(handler is not empty_global_function)


class SpamFunctionsTestCase(unittest.TestCase):
    """
    Test that all spam functions return expected values
    """

    def test_spam_charfield(self):
        class CharFieldTestClass():
            test_charfield = CharField(max_length=1)

        spam = spam_charfield(CharFieldTestClass,
            CharFieldTestClass.test_charfield.__class__,
            'test_charfield')
        self.assertTrue(len(spam) == 1)


class SpamFieldsTestCase(unittest.TestCase):
    """
    Test that the Spamdb.spam_fields function returns a dict with the
    models attributes and their respective spammed values
    """

    def test_spam_fields(self):
        class FieldTestModel(Model):
            test_charfield = CharField()
            test_datefield = DateTimeField()
            test_integerfield = IntegerField()

        sdb = Spamdb(FieldTestModel)

        @sdb.strict_handler(FieldTestModel.test_charfield)
        def spam_testcharfield(model, field_type, field_name):
            return "test"

        @sdb.strict_handler(FieldTestModel.test_datefield)
        def spam_testdatefield(model, field_type, field_name):
            return datetime.date.today()

        @sdb.strict_handler(FieldTestModel.test_integerfield)
        def spam_testintegerfield(model, field_type, field_name):
            return 1

        spammed_attr = sdb.spam_fields(FieldTestModel)

        self.assertEquals(spammed_attr['test_charfield'], "test")
        self.assertEquals(spammed_attr['test_datefield'], datetime.date.today())
        self.assertEquals(spammed_attr['test_integerfield'], 1)

if __name__ == '__main__':
    unittest.main()
