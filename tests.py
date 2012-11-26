import unittest
from spamdb import Spamdb


class TestModel(Model):
	"""
	Base test model class
	"""
    class Meta:
        database = test_db


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
INT = test_db.interpolation


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