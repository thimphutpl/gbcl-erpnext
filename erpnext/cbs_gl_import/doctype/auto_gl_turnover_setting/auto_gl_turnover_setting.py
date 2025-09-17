# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AutoGLTurnoverSetting(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.cbs_gl_import.doctype.auto_gl_turnover_currency_item.auto_gl_turnover_currency_item import AutoGLTurnoverCurrencyItem
		from frappe.types import DF

		table_mxdv: DF.Table[AutoGLTurnoverCurrencyItem]
	# end: auto-generated types
	pass
