# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.dk_integration_utils import fetch_gl_turn_over,fetch_gl_oro_bank
from erpnext.accounts.general_ledger import make_gl_entries
from frappe.utils import flt

class GLTurnoverEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.cbs_gl_import.doctype.turn_over_data.turn_over_data import TurnOverData
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		company: DF.Link | None
		cost_center: DF.Link | None
		currency: DF.Literal["USD"]
		date: DF.Date | None
		items: DF.Table[TurnOverData]
	# end: auto-generated types

	def validate(self):
		self.calculate_total()
	def on_submit(self):
		self.make_journal_entries()

	def calculate_total(self):
		total_debit = 0
		total_credit = 0

		for i in self.items:
			total_credit += flt(i.credit)
			total_debit += flt(i.debit)

		self.total_debit = total_debit
		self.total_credit = total_credit
	
	def make_journal_entries(self):
		je = frappe.new_doc("Journal Entry")
		je.branch = self.branch
		je.voucher_type = "Journal Entry"
		je.naming_series="Journal Voucher"
		je.posting_date = frappe.utils.today()
		je.company = self.company
		je.remark = f"Auto-created from {self.doctype} {self.company}"
		je.multi_currency =1

		for i in self.items:
			account = frappe.db.get_value("GL Account Mapping",{"name":i.gl_number},'account')
			je.append("accounts", {
				"account": account,  
				"debit":i.debit,
				"credit":i.credit,
				"debit_in_account_currency": i.debit,
				"credit_in_account_currency": i.credit,
				"currency":i.currency,
				"cost_center": self.cost_center,
			})
		
		je.save()
		je.submit()

		frappe.msgprint(f"Journal Entry {je.name} created.")



@frappe.whitelist()
def handle_glturnover(date, doc_name):

	response = fetch_gl_turn_over(date).json()
	turnover_data = response["response_data"]["turnover_data"]

	doc = frappe.get_doc("GL Turnover Entry", doc_name)

	# Clear existing items before appending new ones (optional)
	doc.set("items", [])

	for row in turnover_data:
		doc.append("items", {
			"gl_number": row.get("gl_number"),
			"account_name": row.get("account_name"),
			"credit": row.get("item_credit"),
			"debit": row.get("item_debit"),
			"currency": row.get("currency"),
			"gl_date": row.get("gl_date"),
			"begin_balance": row.get("begin_balance"),
			"item_id": row.get("item_id"),
		})

	doc.save()
	return "success"

@frappe.whitelist()
def handle_glturnover_oro(date, doc_name,currency):
	

	response = fetch_gl_oro_bank(date,currency)

	

	doc = frappe.get_doc("GL Turnover Entry", doc_name)

	# Clear existing items before appending new ones (optional)
	doc.set("items", [])

	for account in response:
		flow = account.get('flow', {})  # get the 'flow' dictionary
		in_value = flow.get('in', 0)    # get 'in' value, default 0 if missing
		out_value = flow.get('out', 0)
		net_value = flow.get('net', 0)

		doc.append("items", {
			"gl_number": account.get("accountID"),
			"account_name": account.get("accountName"),
			"credit": in_value,
			"debit": out_value,
			"currency": account.get("currencyCode"),
			# "gl_date": row.get("gl_date"),
			# "begin_balance": row.get("begin_balance"),
			# "item_id": row.get("item_id"),
		})

		# Example: show values using frappe.throw (for testing)
		# frappe.throw(f"Account: {account.get('accountName')}\nIn: {in_value}\nOut: {out_value}\nNet: {net_value}")

	# for row in turnover_data:
	# 	doc.append("items", {
	# 		"gl_number": row.get("gl_number"),
	# 		"account_name": row.get("account_name"),
	# 		"credit": row.get("item_credit"),
	# 		"debit": row.get("item_debit"),
	# 		"currency": row.get("currency"),
	# 		"gl_date": row.get("gl_date"),
	# 		"begin_balance": row.get("begin_balance"),
	# 		"item_id": row.get("item_id"),
	# 	})

	

	doc.save()
	return "success"