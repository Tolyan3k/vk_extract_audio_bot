"""TODO
"""

import pymongo
from bson.objectid import ObjectId


class MongoVariable:
    """TODO"""

    def __init__(
        self,
        mongo_client: pymongo.MongoClient,
        database_name: str,
        collection_name: str,
        object_id: str,
        var_name: str,
    ) -> None:

        self.__mongo_client = mongo_client
        self.__database_name = database_name
        self.__collection_name = collection_name
        self.__object_id = object_id
        self.__var_name = var_name
        self.__var_value = self.__mongo_client[self.__database_name][
            self.__collection_name].find_one(
                {
                    "_id": ObjectId(self.__object_id),
                },
                {
                    "_id": 0,
                    self.__var_name: 1,
                },
            )[self.__var_name]

    # Methods
    def set_value(self, value):
        """TODO

        Args:
        ----
            value (_type_): _description_

        """
        self.__mongo_client[self.__database_name][
            self.__collection_name].update_one(
                {
                    "_id": ObjectId(self.__object_id),
                },
                {
                    "$set": {
                        self.__var_name: value,
                    },
                },
            )
        self.__var_value = value

    def get_value(self):
        """TODO

        Returns
        -------
            _type_: _description_

        """
        return self.__var_value

    # ================================================
    def __repr__(self):
        return self.__var_value.__repr__()

    def __str__(self):
        return self.__var_value.__str__()

    # Binary operators
    def __add__(self, rhs):
        return self.__var_value.__add__(rhs)

    def __sub__(self, rhs):
        return self.__var_value.__sub__(rhs)

    def __mul__(self, rhs):
        return self.__var_value.__mul__(rhs)

    def __truediv__(self, rhs):
        return self.__var_value.__truediv__(rhs)

    def __floordiv__(self, rhs):
        return self.__var_value.__floordiv__(rhs)

    def __mod__(self, rhs):
        return self.__var_value.__mod__(rhs)

    def __pow__(self, rhs):
        return self.__var_value.__pow__(rhs)

    def __rshift__(self, rhs):
        return self.__var_value.__rshift__(rhs)

    def __lshift__(self, rhs):
        return self.__var_value.__lshift__(rhs)

    def __and__(self, rhs):
        return self.__var_value.__and__(rhs)

    def __or__(self, rhs):
        return self.__var_value.__or__(rhs)

    def __xor__(self, rhs):
        return self.__var_value.__xor__(rhs)

    # Comparison operators
    def __lt__(self, rhs):
        return self.__var_value.__lt__(rhs)

    def __gt__(self, rhs):
        return self.__var_value.__gt__(rhs)

    def __le__(self, rhs):
        return self.__var_value.__le__(rhs)

    def __ge__(self, rhs):
        return self.__var_value.__ge__(rhs)

    def __eq__(self, rhs):
        return self.__var_value.__eq__(rhs)

    def __ne__(self, rhs):
        return self.__var_value.__ne__(rhs)

    # Unary operators
    def __isub__(self, rhs):
        self.set_value(self.__var_value.__sub__(rhs))
        self.__var_value = self.__var_value.__sub__(rhs)

        return self

    def __iadd__(self, rhs):
        self.set_value(self.__var_value.__add__(rhs))
        self.__var_value = self.__var_value.__add__(rhs)

        return self

    def __imul__(self, rhs):
        self.set_value(self.__var_value.__mul__(rhs))
        self.__var_value = self.__var_value.__mul__(rhs)

        return self

    def __idiv__(self, rhs):
        self.set_value(self.__var_value.__div__(rhs))
        self.__var_value = self.__var_value.__div__(rhs)

        return self


# ...
