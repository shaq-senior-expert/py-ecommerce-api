# Copyright (c) 2021, Frappe and Contributors
# See license.txt

import frappe
import responses
from frappe.utils import now, now_datetime

from ecommerce_integrations.unicommerce.constants import SETTINGS_DOCTYPE
from ecommerce_integrations.unicommerce.tests.utils import TestCase


class TestUnicommerceSettings(TestCase):
	@responses.activate
	def test_authentication(self):

		responses.add(
			responses.GET,
			"https://demostaging.unicommerce.com/oauth/token?grant_type=password&username=frappe&password=hunter2&client_id=my-trusted-client",
			json=self.load_fixture("authentication"),
			status=200,
			match_querystring=True,
		)

		settings = frappe.get_doc(SETTINGS_DOCTYPE)
		settings.update_tokens()

		self.assertEqual(settings.access_token, "1211cf66-d9b3-498b-a8a4-04c76578b72e")
		self.assertEqual(settings.refresh_token, "18f96b68-bdf4-4c5f-93f2-16e2c6e674c6")
		self.assertEqual(settings.token_type, "bearer")
		self.assertTrue(str(settings.expires_on) > now())

	@responses.activate
	def test_failed_auth(self):

		settings = frappe.get_doc(SETTINGS_DOCTYPE)
		# failure case
		responses.add(
			responses.GET, "https://demostaging.unicommerce.com/oauth/token", json={}, status=401
		)
		self.assertRaises(frappe.ValidationError, settings.update_tokens)

	@responses.activate
	def test_refresh_tokens(self):
		url = "https://demostaging.unicommerce.com/oauth/token?grant_type=refresh_token&client_id=my-trusted-client&refresh_token=REFRESH_TOKEN"
		responses.add(
			responses.GET,
			url,
			json=self.load_fixture("authentication"),
			status=200,
			match_querystring=True,
		)

		settings = frappe.get_doc(SETTINGS_DOCTYPE)
		settings.expires_on = now_datetime()  # to trigger refresh
		settings.refresh_token = "REFRESH_TOKEN"
		settings.renew_tokens(save=False)

		self.assertEqual(settings.access_token, "1211cf66-d9b3-498b-a8a4-04c76578b72e")
		self.assertEqual(settings.refresh_token, "18f96b68-bdf4-4c5f-93f2-16e2c6e674c6")
		self.assertEqual(settings.token_type, "bearer")
		self.assertTrue(str(settings.expires_on) > now())
		self.assertTrue(responses.assert_call_count(url, 1))
