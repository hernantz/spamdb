spamdb
======

Spamdb is a python class that acts like a container (think a list) of peewee models.
It also provides a bunch of methods to spam every database field of your model with a 
randomly generated value. Each method can be overrided with your own spam functions.

The simplest use case would be:

    from spamdb import Spamdb     
    from myapp import models


    # spam all User and Blog db fields and save them to the database
    Spamdb(models.User, models.Blog).run()

The way Spamdb works is as follows:

1. Iterate over self contained models (passed in the _init__ or append)
2. Get a list of peewee.Field type attributes of a models and iterate over this list
3. For each field, try to spam it in this order: 
    * Check if it allows null values.  If so randomly determine to leave the field null or not.
    * Check wether the field  has gotten a choices attribute. If so pick one of these.
    * Check for a strict spam handler for the current field. If found one, call it.
    * Check for a global spam handler for the current field's type. If found one, call it.
    * If none of the above options worked, ignore the current field.
4. Save an instance of the model with the spammed values.

Override the default spam functions with your own

	import spamdb
	import myapp.models
	import peewee

	sdb = spamdb.Spamdb()

	@sdb.global(peewee.CharField)
	def spam_charfield(field):
		return "Hello kitty"

	@sdb.strict(models.User.name):
	def spam_username(field): return "My custom username" sdb.append(models.User) 
	if __name__ == '__main__':
		sdb.run(iterations=100)
