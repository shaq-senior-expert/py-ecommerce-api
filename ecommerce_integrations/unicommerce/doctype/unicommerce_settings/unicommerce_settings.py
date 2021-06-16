# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe import _
from frappe.utils import add_to_date, get_datetime, now_datetime

from ecommerce_integrations.controllers.setting import SettingController
from ecommerce_integrations.unicommerce.constants import SETTINGS_DOCTYPE
from ecommerce_integrations.unicommerce.utils import create_unicommerce_log


class UnicommerceSettings(SettingController):
	def is_enabled(self) -> bool:
		return bool(self.enable_unicommerce)

	def validate(self):
		if not self.is_enabled():
			return

		# TODO: handle 30 days limit
		if not self.access_token or now_datetime() >= get_datetime(self.expires_on):
			try:
				self.update_tokens()
			except:
				create_unicommerce_log(status="Error", message="Failed to authenticate with Unicommerce")

	def renew_tokens(self, save=True):
		if now_datetime() >= get_datetime(self.expires_on):
			try:
				self.update_tokens(grant_type="refresh_token")
			except Exception as e:
				create_unicommerce_log(status="Error", message="Failed to authenticate with Unicommerce")
				raise e
		if save:
			self.save()
			frappe.db.commit()
			self.load_from_db()

	def update_tokens(self, grant_type="password"):
		url = f"https://{self.unicommerce_site}/oauth/token"

		params = {
			"grant_type": grant_type,
			"client_id": "my-trusted-client",  # TODO: make this configurable
		}
		if grant_type == "password":
			params.update({"username": self.username, "password": self.get_password("password")})
		elif grant_type == "refresh_token":
			params.update({"refresh_token": self.get_password("refresh_token")})

		res = requests.get(url, params=params)
		if res.status_code == 200:
			res = res.json()
			self.access_token = res["access_token"]
			self.refresh_token = res["refresh_token"]
			self.token_type = res["token_type"]
			self.expires_on = add_to_date(now_datetime(), seconds=int(res["expires_in"]))
		else:
			res = res.json()
			error, description = res.get("error"), res.get("error_description")
			frappe.throw(_("Unicommerce reported error: <br>{}: {}").format(error, description))
