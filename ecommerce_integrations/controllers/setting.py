from typing import Dict, List, NewType

from frappe.model.document import Document

ERPNextWarehouse = NewType("ERPNextWarehouse", str)
IntegrationWarehouse = NewType("IntegrationWarehouse", str)


class SettingController(Document):
	def is_enabled(self) -> bool:
		"""Check if integration is enabled or not."""
		raise NotImplementedError()

	def get_erpnext_warehouses(self) -> List[ERPNextWarehouse]:
		raise NotImplementedError()

	def get_erpnext_to_integration_wh_mapping(self) -> Dict[ERPNextWarehouse, IntegrationWarehouse]:
		raise NotImplementedError()

	def get_integration_to_erpnext_wh_mapping(self) -> Dict[IntegrationWarehouse, ERPNextWarehouse]:
		raise NotImplementedError()
