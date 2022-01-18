from db import db
from typing import List
import os
import stripe

#MANY TO MANY RELATIONSHIP USING SQLALCHEMY
#This is one method of creating multiple foreign key in one table
# Creating a many to many relationship table with the db instance
# an order can have multiple items, an items can have different orders

# items_to_orders = db.Table(
#     "items_to_orders",
#     db.Column("item_id", db.Integer, db.ForeignKey("items.id")), # which will be a foreign key to items.id
#     db.Column("order_id", db.Integer, db.ForeignKey("orders.id")) # which will be a foreign key to orders.id
#     db.Column("quantity", db.Integer) #this will be the number of items in an order
# )

# concept behind the above table, the content of this table tells us which items is related to which order
# but now this data is not stored in either model, it is stored in a secondary table,
#This is called a secondary table

# [1, 3] item_id 1 and order_id 3
# [3, 5]  item_id 3 and order_id 5

CURRENCY = "usd"

# This is called a secondary model
# we upgraded to this because sqlalchemy works fine with model

class ItemsInOrder(db.Model):
    __tablename__ = "items_in_order"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    quantity = db.Column(db.Integer)

    item = db.relationship("ItemModel")
    order = db.relationship("OrderModel", back_populates="items")


class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)

    #old
    # items = db.relationship("ItemModel", seconadry=items_to_orders, lazy="dynamic")
    items = db.relationship("ItemsInOrder", back_populates="order")
    # The reason for backpopulates is because after we created an order model, we can add an item
    # which eventually makes changes in one reflect in the other

    @property
    def description(self) -> str:
        """
        Generates a simple string representing this order, in the format of "5x chair, 2x table"
        """
        item_counts = [f"{item_data.quantity}x {item_data.item.name}" for item_data in self.items]
        return ",".join(item_counts)

    @property   #we added this property to make this method a variable because it doesn't take any arguments and we want to pretend as if is a variable
    def amount(self) -> int:
        """
        Calculates the total amount to charge for this order.
        Assumes item price is in USD–multi-currency becomes much tricker!
        :return int: total amount of cents to be charged in this order.x`
        """
        return int(sum([item_data.item.price * item_data.quantity for item_data in self.items]) * 100)


    #Benefit of this is that you can get an order to be related to many items
    @classmethod
    def find_all(cls) -> List["OrderModel"]:
        return cls.query.all()

    @classmethod
    def find_by_id(cls, _id: int) -> "OrderModel":
        return cls.query.filter_by(id=_id).first()

    def charge_with_stripe(self, token: str) -> stripe.Charge:
        # Set your secret key: remember to change this to your live secret key in production

        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        return stripe.Charge.create(
            amount=self.amount,  #that is why we can use self.amount instaed of using amount() because i can 
            currency=CURRENCY,
            description=self.description,
            source=token
        )

    def set_status(self, new_status: str) -> None:
        """
        Sets the new status for the order and saves to the database—so that an order is never not committed to disk.
        :param new_status: the new status for this order to be saved.
        """
        self.status = new_status
        self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
        