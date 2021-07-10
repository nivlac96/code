from datetime import date, timedelta
import pytest
from model import Product, Order, OrderLine, Batch, allocate

# from model import ...

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

### Helper functions

# not the ideal way to generate ids, but without static vars its good enough for now
def create_order_line_and_batch(_id: int, _product: Product, _batch_qty: int, _order_qty: int):
    return (Batch(_id, _product, _batch_qty, tomorrow),
            OrderLine(_id, _product, _order_qty))


def can_allocate(_batch: Batch, _order_line: OrderLine):
    _batch.allocate(_order_line)
    return _order_line in _batch.allocated


### Tests

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, order_line = create_order_line_and_batch(1, Product.LAMP, 5, 2)
    start_qty = batch.available_qty
    batch.allocate(order_line)

    assert(batch.available_qty == start_qty - order_line.qty)


def test_can_allocate_if_available_greater_than_required():
    batch, order_line = create_order_line_and_batch(1, Product.LAMP, 5, 2)
    batch.allocate(order_line)

    assert(order_line in batch.allocated)


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = create_order_line_and_batch(1, Product.LAMP, 5, 7)
    batch.allocate(order_line)

    assert (order_line not in batch.allocated)


def test_can_allocate_if_available_equal_to_required():
    batch, order_line = create_order_line_and_batch(1, Product.LAMP, 5, 5)
    batch.allocate(order_line)

    assert (order_line in batch.allocated)


def test_cannot_allocate_if_skus_dont_match():
    batch = Batch(1, Product.LAMP, 5, tomorrow)
    order_line = OrderLine(2, Product.CHAIR, 2)

    assert(can_allocate(batch, order_line) is False)


def test_can_only_deallocate_allocated_line():
    batch, order_line = create_order_line_and_batch(1, Product.LAMP, 5, 5)
    batch.deallocate(order_line)

    assert(batch.available_qty == 5)


def test_allocate_is_idempotent():
    batch, order_line = create_order_line_and_batch(1, Product.LAMP, 5, 1)
    batch.allocate(order_line)
    batch.allocate(order_line)

    assert(batch.available_qty == 4)


def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch(1, Product.LAMP, 5, None)
    arriving_batch = Batch(2, Product.LAMP, 5, today)
    line = OrderLine(3, Product.LAMP, 2)

    allocate(line, (warehouse_batch, arriving_batch))

    assert warehouse_batch.available_qty == 3
    assert arriving_batch.available_qty == 5


def test_prefers_earlier_batches():
    sooner_batch = Batch(1, Product.LAMP, 5, today)
    later_batch = Batch(2, Product.LAMP, 5, tomorrow)
    line = OrderLine(3, Product.LAMP, 2)

    allocate(line, (sooner_batch, later_batch))

    assert sooner_batch.available_qty == 3
    assert later_batch.available_qty == 5
