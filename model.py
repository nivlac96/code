# In this file I opted to name parameters with a '_' prefix. It might be better
# to reserve this for private variables

from enum import Enum
from dataclasses import dataclass


class Product(Enum):
    LAMP = 1,
    CHAIR = 2,
    TABLE = 3


# an orderline is a 'value object', it is identified by the data it holds, it itself has no identifier
# they have 'value equality', meaning that two of these with identical properties are considered equal
@dataclass(frozen=True)
class OrderLine:

    order_id: int
    sku: Product
    qty: int

    # This method is not required because of the dataclass decorator above this class
    # def __init__(self, _order_id, _sku, _quantity):
    #     self.order_id = _order_id
    #     self.sku = _sku
    #     self.qty = _quantity


class Order:

    reference: int
    lines: list[OrderLine]

    def __init__(self, _ref, _lines=None):
        self.reference = _ref
        if _lines is None:
            self.lines = []
        else:
            self.lines = _lines

    def add_line(self, line: OrderLine):
        if line not in self.lines:
            self.lines.append(line)


class Batch:

    reference: int
    sku: Product
    available_qty: int
    eta: int
    allocated: list[OrderLine]

    def __init__(self, _ref, _sku, _available_qty, _eta):
        self.reference = _ref
        self.sku = _sku
        self.available_qty = _available_qty
        self.eta = _eta  # eta of None implies the batch is already warehoused
        self.allocated = []

    def allocate(self, _line: OrderLine):
        if self.can_allocate(_line):
            self.allocated.append(_line)
            self.available_qty -= _line.qty

    def deallocate(self, _line: OrderLine):
        if _line in self.allocated:
            self.allocated.remove(_line)
            self.available_qty += _line.qty

    def can_allocate(self, _line):
        return (_line.qty <= self.available_qty and
                _line.sku == self.sku and
                _line not in self.allocated)

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    # As an identifiable entity, a Batch should be hashed based on it's identifiable
    # property, if at all.
    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        elif other.eta is None:
            return True
        return self.eta > other.eta


class OutOfStock(Exception):
    pass


# This standalone method for our model is outside of the object-oriented framework
# Python is multi-paradigm
def allocate(_line: OrderLine, _batches: list[Batch]):
    """allocate the line to the soonest available batch"""
    try:
        batch = next(b for b in sorted(_batches) if b.can_allocate(_line))
        batch.allocate(_line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Item is out of stock: {_line.sku}")
