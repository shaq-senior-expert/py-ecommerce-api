from collections import Counter
from typing import Dict

import frappe
from frappe.utils import cint, now
from shopify.resources import InventoryLevel, Variant

from ecommerce_integrations.controllers.inventory import (
	get_inventory_levels,
	update_inventory_sync_status,
)
from ecommerce_integrations.shopify.connection import temp_shopify_session
from ecommerce_integrations.shopify.constants import MODULE_NAME, SETTING_DOCTYPE
from ecommerce_integrations.shopify.utils import create_shopify_log


def update_inventory_on_shopify() -> None:
	"""Upload stock levels from ERPNext to Shopify.

	Called by scheduler on configured interval.
	"""
	setting = frappe.get_doc(SETTING_DOCTYPE)

	if not setting.is_enabled() or not setting.update_erpnext_stock_levels_to_shopify:
		return

	warehous_map = setting.get_erpnext_to_integration_wh_mapping()
	inventory_levels = get_inventory_levels(tuple(warehous_map.keys()), MODULE_NAME)

	if inventory_levels:
		upload_inventory_data_to_shopify(inventory_levels, warehous_map)


@temp_shopify_session
def upload_inventory_data_to_shopify(inventory_levels, warehous_map) -> None:
	synced_on = now()

	for d in inventory_levels:
		d.shopify_location_id = warehous_map[d.warehouse]

		try:
			variant = Variant.find(d.variant_id)
			inventory_id = variant.inventory_item_id

			InventoryLevel.set(
				location_id=d.shopify_location_id,
				inventory_item_id=inventory_id,
				# shopify doesn't support fractional quantity
				available=cint(d.actual_qty) - cint(d.reserved_qty),
			)
			update_inventory_sync_status(d.ecom_item, time=synced_on)
			d.status = "Success"
		except Exception as e:
			create_shopify_log(method="update_inventory_on_shopify", status="Error", exception=e)
			d.status = "Failed"

	_log_inventory_update_status(inventory_levels)


def _log_inventory_update_status(inventory_levels) -> None:
	"""Create log of inventory update."""
	log_message = "variant_id,location_id,status\n"

	log_message += "\n".join(
		f"{d.variant_id},{d.shopify_location_id},{d.status}" for d in inventory_levels
	)

	stats = Counter([d.status for d in inventory_levels])

	percent_successful = stats["Success"] / (stats["Success"] + stats["Failed"])

	if percent_successful == 0:
		status = "Failed"
	elif percent_successful < 1:
		status = "Partial Success"
	else:
		status = "Success"

	log_message = f"Updated {percent_successful * 100}% items\n\n" + log_message

	create_shopify_log(method="update_inventory_on_shopify", status=status, message=log_message)
