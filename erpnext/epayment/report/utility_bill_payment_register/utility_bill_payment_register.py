# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}
	data = get_data(filters)
	columns = get_columns(data)
	return columns, data

def get_columns(data):
	columns = [
		{
			"label": _("Utility Bill"),
			"fieldname": "utility_bill",
			"fieldtype": "Link",
			"options": "Utility Bill",
			"width": 140,
		},
		{
			"label": _("Utility Service Type"),
			"fieldname": "utility_service_type",
			"fieldtype": "Link",
			"options": "Utility Service Type",
			"width": 150,
		},
		{
			"label": _("Party"),
			"fieldname": "party",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"width": 150,
		},
		
		{
			"label": _("PI Number"),
			"fieldname": "pi_number",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Payment Status"),
			"fieldname": "payment_status",
			"fieldtype": "Data",
			"width": 150,
		},
		# ("Branch Expense Account") + ":Data:200",
		# ("Paid From Bank Account") + ":Data:200",
		# ("Debit Account") + ":Link/Account:200",
		# ("Unique Identity Code") + ":Data:100",
		# ("Payment Status") + ":Data:100",
		# ("Payment API Response") + ":Data:400",
		# ("Create Direct Payment") + ":Check:100",
		# ("TDS Applicable") + ":Check:100",
	]
	return columns

def get_data(filters):
	data = frappe.db.sql("""
		SELECT 
			ut.name as utility_bill, ut.posting_date, uti.utility_service_type, uti.party, ut.expense_account, ut.bank_account, uti.debit_account, uti.consumer_code, uti.outstanding_amount, uti.payment_status, uti.payment_response_msg, uti.create_direct_payment, uti.tds_applicable, uti.pi_number
		FROM `tabUtility Bill` ut, `tabUtility Bill Item` uti 
		WHERE ut.name=uti.parent
		
	""", as_dict=True)
	return data