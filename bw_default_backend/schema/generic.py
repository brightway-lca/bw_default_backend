from peewee import TextField, Model


class UncertaintyType(Model):
    label = TextField()
