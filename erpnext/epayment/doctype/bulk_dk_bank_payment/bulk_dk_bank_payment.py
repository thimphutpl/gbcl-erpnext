# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.dk_integration_utils import fetch_exchange_rate,account_inquiry
import re

class BulkDKBankPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.epayment.doctype.bulk_dk_bank_payment_item.bulk_dk_bank_payment_item import BulkDKBankPaymentItem
		from frappe.types import DF

		acc_status_details: DF.Data | None
		amended_from: DF.Link | None
		bank_account_no: DF.Data | None
		bank_balance: DF.Currency
		bank_balance_usd: DF.Currency
		company: DF.Link | None
		inquiry_id: DF.Data | None
		paid_from: DF.Link | None
		payer_name: DF.Data | None
		posting_date: DF.Date | None
		total_amount: DF.Currency
		transaction: DF.Table[BulkDKBankPaymentItem]
		transaction_code: DF.Link
		transaction_no: DF.DynamicLink | None
		transaction_type: DF.Literal["Payroll Entry"]
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.epayment.doctype.bulk_dk_bank_payment_item.bulk_dk_bank_payment_item import BulkDKBankPaymentItem
		from frappe.types import DF

		acc_status_details: DF.Data | None
		amended_from: DF.Link | None
		bank_account_no: DF.Data | None
		bank_balance: DF.Currency
		company: DF.Link | None
		inquiry_id: DF.Data | None
		paid_from: DF.Link | None
		payer_name: DF.Data | None
		posting_date: DF.Date | None
		total_amount: DF.Currency
		transaction: DF.Table[BulkDKBankPaymentItem]
		transaction_no: DF.DynamicLink | None
		transaction_type: DF.Literal["Payroll Entry"]
	def on_submit(self):
		frappe.log_error("on_submit", self.name)
		frappe.enqueue(
			method="erpnext.epayment.doctype.bulk_dk_bank_payment.bulk_dk_bank_payment.create_bank_payments",
			queue="long",
			timeout=600,
			bulk_doc_name=self.name
		)



	@frappe.whitelist()
	def get_entries(self):
		# frappe.throw("hi my friends, she ill ")
		data1= frappe.db.sql("""
			select employee, gross_pay, net_pay,currency from `tabSalary Slip` 
			where payroll_entry='{}';
			""".format(self.transaction_no),
			as_dict=True,
		)

		currency = frappe.db.get_value(
				"Transaction Code",
				self.transaction_code,
				"currency"
			)
		trans_code = frappe.db.get_value(
				"Transaction Code",
				self.transaction_code,
				"trans_code"
			)
		fx_rate_value = 1
		if currency and currency.upper() != "BTN":
			result=fetch_exchange_rate(self.transaction_code)
			data = result.json()
			if data.get("response_code") != "0000":
				
				frappe.throw("Failed to fetch exchange rate: {}".format(
					data.get("response_detail", "No details provided")
				))

			fx_rate = data.get("response_data", {}).get("exchange_rates", [])
		  # default fallback

			for rate in fx_rate:
				if rate.get("currency_code", "").upper() == currency.upper():
					fx_rate_value = float(rate.get("buy_rate") or 1)
					break
						
			
	
		for row in data1:
			bank_name = frappe.db.get_value("Employee",row.employee,"bank_name")
			bank_ac_no = frappe.db.get_value("Employee",row.employee,"bank_ac_no")
		
			employee_name = frappe.db.get_value("Employee",row.employee,"employee_name")
		
			if not bank_ac_no:
				frappe.throw(
					"Bank account number is missing for employee: {}".format(employee_name)
				)
			bank_ac_no = re.sub(r"\s+", "", bank_ac_no)
			if trans_code == "3110R":
				if not bank_ac_no.startswith("1201"):
					frappe.throw(
						"For USD-USD transactions (3110R), only accounts starting with '1201' are allowed."
					)
			
			if bank_name == "DK":
				account_inquiry(bank_ac_no)
			

			row["bank_ac_no"] = bank_ac_no
			row["bank_name"] = bank_name
			row["employee_name"] = employee_name
			row["currency_code"] = currency
			row["fx_rate"] = fx_rate_value 

		return data1
		# frappe.throw(frappe.as_json(data1))


def create_bank_payments(bulk_doc_name):
	# frappe.throw(str(bulk_doc_name))
	bulk_doc = frappe.get_doc("Bulk DK Bank Payment", bulk_doc_name)
	created_payments = []

	for i in bulk_doc.transaction:

		# Prevent duplicate creation
		if i.dk_bank_payment:
			continue

		try:
			doc = frappe.new_doc("DK Bank Payment")
			doc.company = bulk_doc.company
			# doc.transaction_code = "Intrabank transfer"
			doc.transaction_code = bulk_doc.transaction_code
			doc.transaction_type = "Bulk DK Bank Payment"
			doc.paid_from = bulk_doc.paid_from
			doc.bank_balance_usd = bulk_doc.bank_balance_usd
			doc.bank_balance = bulk_doc.bank_balance
			doc.bank_account_no = bulk_doc.bank_account_no
			doc.transaction_no = bulk_doc.name
	

			doc.append("transaction", {
				"beneficiary_account_no": i.beneficiary_account_no,
				"beneficiary_name": i.beneficiary_name,
				"amount": i.amount,
				"bank_name": i.bank_name,
				"fx_rate": i.fx_rate,
			})
			

			# doc.account_enquire()
			doc.insert(ignore_permissions=True)
			doc.on_submit()
			frappe.db.commit()

			# Link created payment back to child row
			i.db_set("dk_bank_payment", doc.name)

			created_payments.append(doc.name)

		except Exception as e:
			frappe.log_error(
				title="Bulk DK Bank Payment Error",
				message=f"Row: {i.name}\nError: {str(e)}"
			)
			raise

	return created_payments

			

