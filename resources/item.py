# from flask_restful import Resource, reqparse
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, fresh_jwt_required
from marshmallow import ValidationError
from models.item import ItemModel
from schemas.item import ItemSchema
from libs.strings import gettext

# BLANK_ERROR = "'{}' cannot be blank."  as the parser goes, we are no longer in need of the blank error
NAME_ALREADY_EXISTS = "An item with name '{}' already exists."
ERROR_INSERTING = "An error occurred while inserting the item."
ITEM_NOT_FOUND = "Item not found."
ITEM_DELETED = "Item deleted."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)  # instead of passing a single item model to d schema, we can pass it as a list


class Item(Resource):
    # parser = reqparse.RequestParser()
    # parser.add_argument(
    #     "price", type=float, required=True, help=BLANK_ERROR.format("price")
    # )
    # parser.add_argument(
    #     "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    # )

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):       # this endpoint gives us, /item/chair fo exaple
        if ItemModel.find_by_name(name):
            return {"message": gettext("item_name_exists").format(name)}, 400

        # data = cls.parser.parse_args()
        item_json = request.get_json()   # the request comes from flask, this is thw json payload, this json paylaod we
        # have other info  mainly price and store_id
        item_json["name"] = name

        # try:
        item = item_schema.load(item_json)  # when we do item schema load, we are going to pass price and store_id
        # except ValidationError as err:
        #     return err.messages, 400
        try:
            item.save_to_db()
        except:
            return {"message": gettext("item_error_inserting")}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": gettext("item_deleted")}, 200
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    def put(cls, name: str):
        # data = cls.parser.parse_args() takes arg that are coming through json
        item_json = request.get_json()

        item = ItemModel.find_by_name(name)  # then check if the item exist

        if item:   # if true it update it
            # item.price = data["price"]
            item.price = item_json["price"]
        else:  # else it creates a new item
            item_json["name"] = name

            # try:
            item = item_schema.load(item_json)  # when we do item schema load, we are going to pass price and
                # store_id
            # except ValidationError as err:
            #     return err.messages, 400

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        # return {"items": [item.json() for item in ItemModel.find_all()]}, 200
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
    # item_list_schema returns a list of each items
