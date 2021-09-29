import base64
import unittest

import frappe
import responses
from erpnext.stock.doctype.stock_entry.stock_entry_utils import make_stock_entry

from ecommerce_integrations.unicommerce.constants import (
	FACILITY_CODE_FIELD,
	INVOICE_CODE_FIELD,
	ORDER_CODE_FIELD,
	SHIPPING_PACKAGE_CODE_FIELD,
)
from ecommerce_integrations.unicommerce.invoice import bulk_generate_invoices, create_sales_invoice
from ecommerce_integrations.unicommerce.order import create_order, get_taxes
from ecommerce_integrations.unicommerce.tests.test_client import TestCaseApiClient


class TestUnicommerceInvoice(TestCaseApiClient):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()

	def test_get_tax_lines(self):
		invoice = self.load_fixture("invoice-SDU0010")["invoice"]
		channel_config = frappe.get_doc("Unicommerce Channel", "RAINFOREST")

		taxes = get_taxes(invoice["invoiceItems"], channel_config)

		created_tax = sum(d["tax_amount"] for d in taxes)
		expected_tax = sum(item["totalTax"] for item in invoice["invoiceItems"])

		self.assertAlmostEqual(created_tax, expected_tax)

	@unittest.skip("Too similar to e2e test down below")
	def test_create_invoice(self):
		"""Use mocked invoice json to create and assert synced fields"""
		order = self.load_fixture("order-SO5906")["saleOrderDTO"]
		so = create_order(order, client=self.client)

		si_data = self.load_fixture("invoice-SDU0026")["invoice"]
		label = self.load_fixture("invoice_label_response")["label"]

		si = create_sales_invoice(si_data=si_data, so_code=so.name, shipping_label=label)

		self.assertEqual(si.get(ORDER_CODE_FIELD), order["code"])
		self.assertEqual(si.get(FACILITY_CODE_FIELD), "Test-123")
		self.assertEqual(si.get(INVOICE_CODE_FIELD), si_data["code"])
		self.assertEqual(si.get(SHIPPING_PACKAGE_CODE_FIELD), si_data["shippingPackageCode"])

		self.assertAlmostEqual(si.grand_total, 7028)
		self.assertEqual(si.update_stock, 0)

		# check that pdf invoice got synced
		attachments = frappe.get_all(
			"File", fields=["name", "file_name"], filters={"attached_to_name": si.name}
		)
		self.assertGreaterEqual(
			len(attachments), 2, msg=f"Expected 2 attachments, found: {str(attachments)}"
		)

	def test_end_to_end_invoice_generation(self):
		"""Full invoice generation test with mocked responses."""

		from ecommerce_integrations.unicommerce import invoice

		si_data = self.load_fixture("invoice-SDU0026")["invoice"]

		# HACK to allow invoicing test
		invoice.INVOICED_STATE.append("CREATED")
		self.responses.add(
			responses.POST,
			"https://demostaging.unicommerce.com/services/rest/v1/oms/shippingPackage/createInvoiceAndAllocateShippingProvider",
			status=200,
			json=self.load_fixture("create_invoice_and_assign_shipper"),
			match=[responses.json_params_matcher({"shippingPackageCode": "TEST00949"})],
		)
		self.responses.add(
			responses.POST,
			"https://demostaging.unicommerce.com/services/rest/v1/invoice/details/get",
			status=200,
			json=self.load_fixture("invoice-SDU0026"),
			match=[responses.json_params_matcher({"shippingPackageCode": "TEST00949", "return": False})],
		)
		self.responses.add(
			responses.GET,
			"https://example.com",
			status=200,
			body=base64.b64decode(self.load_fixture("invoice_label_response")["label"]),
		)

		order = self.load_fixture("order-SO5906")["saleOrderDTO"]
		so = create_order(order, client=self.client)
		make_stock_entry(item_code="MC-100", qty=15, to_warehouse="Stores - WP", rate=42)

		bulk_generate_invoices(sales_orders=[so.name], client=self.client)

		sales_invoice_code = frappe.db.get_value("Sales Invoice", {INVOICE_CODE_FIELD: "SDU0026"})

		if not sales_invoice_code:
			self.fail("Sales invoice not generated")

		si = frappe.get_doc("Sales Invoice", sales_invoice_code)

		self.assertEqual(si.get(ORDER_CODE_FIELD), order["code"])
		self.assertEqual(si.get(FACILITY_CODE_FIELD), "Test-123")
		self.assertEqual(si.get(INVOICE_CODE_FIELD), si_data["code"])
		self.assertEqual(si.get(SHIPPING_PACKAGE_CODE_FIELD), si_data["shippingPackageCode"])

		self.assertAlmostEqual(si.grand_total, 7028)

		# check that pdf invoice got synced
		attachments = frappe.get_all(
			"File", fields=["name", "file_name"], filters={"attached_to_name": si.name}
		)
		self.assertGreaterEqual(
			len(attachments), 2, msg=f"Expected 2 attachments, found: {str(attachments)}"
		)
