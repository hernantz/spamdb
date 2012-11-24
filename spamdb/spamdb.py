import peewee


class Spamdb(list):

    # shortcut to append
    add = list.append

    def __init__(self, *args):
        for a in args:
            self.append(a)

    def run(self):
        for model in self.__iter__():
            print model
