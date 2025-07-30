# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from frappe.model.document import Document


class Branch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.branch_bank_account.branch_bank_account import BranchBankAccount
		from frappe.types import DF

		branch: DF.Data
		branch_bank_account: DF.Table[BranchBankAccount]
		company: DF.Link
		cost_center: DF.Link
		disabled: DF.Check
		expense_bank_account: DF.Link | None
		holiday_list: DF.Link | None
		revenue_bank_account: DF.Link | None
	# end: auto-generated types

	pass
