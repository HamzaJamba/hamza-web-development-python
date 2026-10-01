from decimal import Decimal
from rest_framework.test import APITestCase
from config.testutils import make_vendor, make_product, make_user, CHECKOUT
from orders.models import Order, OrderItem
from catalog.models import Product


class CheckoutTests(APITestCase):
    def setUp(self):
        self.vendor = make_vendor(commission=10)
        self.product = make_product(self.vendor, "Kurta", "1000", stock=10)
        self.user = make_user("buyer@test.pk")
        self.client.force_authenticate(self.user)

    def checkout(self, items=None, **over):
        body = {**CHECKOUT, "items": items or [{"product": self.product.id, "quantity": 2}], **over}
        return self.client.post("/api/orders/checkout/", body, format="json")

    def test_checkout_computes_totals_from_database_prices(self):
        r = self.checkout()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Decimal(r.data["subtotal"]), Decimal("2000"))
        self.assertEqual(Decimal(r.data["shipping_fee"]), Decimal("250"))
        self.assertEqual(Decimal(r.data["total"]), Decimal("2250"))

    def test_free_shipping_over_threshold(self):
        r = self.checkout([{"product": self.product.id, "quantity": 6}])
        self.assertEqual(Decimal(r.data["shipping_fee"]), Decimal("0"))

    def test_stock_is_reduced_and_commission_recorded(self):
        self.checkout()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        item = OrderItem.objects.get()
        self.assertEqual(item.commission, Decimal("200.00"))

    def test_cannot_buy_more_than_stock(self):
        r = self.checkout([{"product": self.product.id, "quantity": 11}])
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_duplicate_lines_are_merged(self):
        r = self.checkout([{"product": self.product.id, "quantity": 2}, {"product": self.product.id, "quantity": 3}])
        self.assertEqual(r.data["items"][0]["quantity"], 5)

    def test_card_payment_success_marks_paid(self):
        r = self.checkout(payment_method="card", card_number="4242 4242 4242 4242")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["payment_status"], "paid")

    def test_declined_card_rolls_everything_back(self):
        r = self.checkout(payment_method="card", card_number="4000 0000 0000 0002")
        self.assertEqual(r.status_code, 402)
        self.assertEqual(Order.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_invalid_card_number_rejected(self):
        r = self.checkout(payment_method="card", card_number="1234")
        self.assertEqual(r.status_code, 402)

    def test_login_required(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.checkout().status_code, 401)

    def test_customer_only_sees_own_orders(self):
        self.checkout()
        self.client.force_authenticate(make_user("other@test.pk"))
        self.assertEqual(self.client.get("/api/orders/").data["count"], 0)


class FulfilmentTests(APITestCase):
    def setUp(self):
        self.v1 = make_vendor("a@test.pk", "Stall A")
        self.v2 = make_vendor("b@test.pk", "Stall B")
        self.p1 = make_product(self.v1, "A thing", "500", stock=5)
        self.p2 = make_product(self.v2, "B thing", "700", stock=5)
        self.buyer = make_user("buyer@test.pk")
        self.client.force_authenticate(self.buyer)
        r = self.client.post("/api/orders/checkout/", {**CHECKOUT, "items": [
            {"product": self.p1.id, "quantity": 1}, {"product": self.p2.id, "quantity": 1}]}, format="json")
        self.order = Order.objects.get(pk=r.data["id"])

    def set_status(self, vendor, item, status):
        self.client.force_authenticate(vendor.owner)
        return self.client.post(f"/api/orders/items/{item.id}/status/", {"status": status})

    def test_vendor_only_sees_own_lines(self):
        self.client.force_authenticate(self.v1.owner)
        r = self.client.get("/api/orders/vendor-items/")
        self.assertEqual([i["product_name"] for i in r.data["results"]], ["A thing"])

    def test_vendor_cannot_touch_another_stalls_item(self):
        item_b = self.order.items.get(vendor=self.v2)
        self.assertEqual(self.set_status(self.v1, item_b, "packed").status_code, 404)

    def test_invalid_transition_rejected(self):
        item_a = self.order.items.get(vendor=self.v1)
        self.assertEqual(self.set_status(self.v1, item_a, "delivered").status_code, 400)

    def test_order_status_follows_the_stalls(self):
        a, b = self.order.items.get(vendor=self.v1), self.order.items.get(vendor=self.v2)
        self.set_status(self.v1, a, "packed")
        self.order.refresh_from_db(); self.assertEqual(self.order.status, "processing")
        self.set_status(self.v1, a, "shipped")
        self.order.refresh_from_db(); self.assertEqual(self.order.status, "shipped")
        for step in ("packed", "shipped", "delivered"):
            self.set_status(self.v2, b, step)
        self.set_status(self.v1, a, "delivered")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "delivered")
        self.assertEqual(self.order.payment_status, "paid")  # cash collected on delivery

    def test_customer_can_cancel_before_packing_and_stock_returns(self):
        self.client.force_authenticate(self.buyer)
        r = self.client.post(f"/api/orders/{self.order.id}/cancel/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "cancelled")
        self.p1.refresh_from_db(); self.assertEqual(self.p1.stock, 5)

    def test_cannot_cancel_after_a_stall_packs(self):
        self.set_status(self.v1, self.order.items.get(vendor=self.v1), "packed")
        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.post(f"/api/orders/{self.order.id}/cancel/").status_code, 400)

    def test_vendor_dashboard_totals_exclude_cancelled(self):
        self.client.force_authenticate(self.v1.owner)
        d = self.client.get("/api/dashboard/vendor/").data
        self.assertEqual(d["revenue"], 500.0)
        self.assertEqual(d["commission"], 50.0)
        self.assertEqual(d["net"], 450.0)
        self.assertEqual(len(d["daily"]), 14)

    def test_customer_cannot_open_vendor_dashboard(self):
        self.client.force_authenticate(self.buyer)
        self.assertEqual(self.client.get("/api/dashboard/vendor/").status_code, 403)
