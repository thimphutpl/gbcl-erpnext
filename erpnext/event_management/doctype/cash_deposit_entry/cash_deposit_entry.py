# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe import _
from frappe.utils import flt, now_datetime


class CashDepositEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.event_management.doctype.cash_deposit_entry_item.cash_deposit_entry_item import CashDepositEntryItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		company: DF.Link | None
		cost_center: DF.Link | None
		from_date: DF.Date | None
		items: DF.Table[CashDepositEntryItem]
		journal_entry: DF.Data | None
		journal_entry_status: DF.Data | None
		location: DF.Link
		posting_date: DF.Date | None
		to_date: DF.Date | None
		total_amount: DF.Currency
	# end: auto-generated types

	def on_submit(self):
		self.post_cash_entry()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("GL Entry", "Payment Ledger Entry")
	
	@frappe.whitelist()
	def get_transaction_detail(self):
		try:
			data = frappe.db.sql("""
				SELECT t1.name AS reference_name, t1.cashier, t1.posting_date, t2.amount AS cash_amount
				FROM `tabFee Closing Entry` t1
				INNER JOIN `tabPayment Method Detail` t2 ON t1.name = t2.parent
				WHERE t1.location = %s 
					AND t1.docstatus = 1
					AND t2.mode_of_payment = 'Cash'
					AND t1.posting_date BETWEEN %s AND %s
					AND NOT EXISTS (
						SELECT 1 FROM `tabCash Deposit Entry Item` t3
						WHERE t1.name = t3.reference_name
					)
			""", (self.location, self.from_date, self.to_date), as_dict=True)
			return data
		except Exception as e:
			frappe.log_error(f"Error in get_transaction_detail: {e}")
			return []

	def post_cash_entry(self):
		cash_account = frappe.db.get_value("Company", self.company, "default_cash_account")
		bank_account = frappe.db.get_value("Company", self.company, "default_bank_account")

		if not cash_account:
			frappe.throw(
				"Default Bank Account is not set for {}. Please configure it in the company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		if not bank_account:
			frappe.throw(
				"Default Bank Account is not set for {}. Please configure it in the company.".format(
					frappe.get_desk_link("Company", self.company)
				),
				title="Missing Account"
			)

		# Posting Journal Entry
		accounts = []
		accounts.append({
			"account": bank_account,
			"debit_in_account_currency": flt(self.total_amount),
			"cost_center": self.cost_center,
			"reference_type": self.doctype,
			"reference_name": self.name,
		})

		accounts.append({
			"account": cash_account,
			"credit_in_account_currency": flt(self.total_amount),
			"cost_center": self.cost_center,
		})

		je = frappe.new_doc("Journal Entry")
		
		voucher_type = "Cash Entry"
		naming_series = "Cash Receipt Voucher"
		
		je.update({
				"doctype": "Journal Entry",
				"voucher_type": voucher_type,
				"naming_series": naming_series,
				"title": "Bank to Cash - "+self.location,
				"user_remark": "Bank to cash - "+self.location,
				"posting_date": self.posting_date,
				"company": self.company,
				"accounts": accounts,
				"branch": self.branch
		})

		je.save(ignore_permissions = True)
		je.submit()
		self.db_set("journal_entry", je.name)
		self.db_set("journal_entry_status", "Deposit to accounts for on {0}".format(now_datetime().strftime('%Y-%m-%d %H:%M:%S')))
		frappe.msgprint(_('{} posted to accounts').format(frappe.get_desk_link(je.doctype,je.name)))
