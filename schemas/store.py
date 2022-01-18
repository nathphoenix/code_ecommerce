from ma import ma
from models.store import StoreModel

# we have to import this because of the relationship between ItemModel and StoreModel
from models.item import ItemModel
from schemas.item import ItemSchema

# we dont want to inherit from Schema because that comes from marshmallow and it doesn't
# have enough information about the flask app that we have have linked with flask-marshmallow


class StoreSchema(ma.ModelSchema):
    # from store model, store contains many items
    items = ma.Nested(ItemSchema, many=True)  # means items property in the store is something that is nested inside the
    # store and it contains many item schema, we are only dumping but not loading

    class Meta:
        model = StoreModel    # this is extending the functionality of marshmallow schema and link up the user model
        dump_only = ("id",)
        include_fk = True

        # must be included since we are returning the store_id as it is a foreign key