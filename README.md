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

Override the default spam functions with your own

	import spamdb
	import myapp.models
	import peewee

	sdb = spamdb.Spamdb()

	@sdb.global(peewee.CharField)
	def spam_charfield(field):
		return "Hello kitty"

	@sdb.strict(models.User.name):
	def spam_username(field):
		return "My custom username"

	sdb.append(models.User)

	if __name__ == '__main__':
		sdb.run(iterations=100)
