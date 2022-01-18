from ma import ma
from models.item import ItemModel

# we have to iport this because of the relationship between ItemMoel and StoreModel
from models.store import StoreModel

# we dont want to inherit from Schema because that comes from marshmallow and it doesn't
# have enough information about the flask app that we have have linked with flask-marshmallow


class ItemSchema(ma.ModelSchema):
    # this is weird in python, defining a class inside a class but you can do it with marshmallow
    # You can say a field is for loading the data and not for dumping it
    class Meta:
        model = ItemModel    # this is extending the functionality of marshmallow schema and link up the user model
        load_only = ("store",)  # meaning the store field is only for loading the data, it should not be returned
                                   # when dumping  the data
        dump_only = ("id",)
        include_fk = True
        # must be included since we are returning the store_id as it is a foreign key