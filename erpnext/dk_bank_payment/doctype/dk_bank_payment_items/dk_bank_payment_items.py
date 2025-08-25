# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DKBankPaymentItems(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		bank_name: DF.Link | None
		beneficiary_account_no: DF.Data | None
		beneficiary_name: DF.Data | None
		currency_code: DF.Link | None
		description: DF.SmallText | None
		employee: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		supplier: DF.Link | None
	# end: auto-generated types
	pass
