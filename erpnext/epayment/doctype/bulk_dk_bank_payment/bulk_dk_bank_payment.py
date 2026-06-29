# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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
			timeout=60,
			bulk_doc_name=self.name
		)



	@frappe.whitelist()
	def get_entries(self):
		# frappe.throw("hi my friends, she ill ")
		data1= frappe.db.sql("""
			select employee, gross_pay, net_pay from `tabSalary Slip` 
			where payroll_entry='{}';
			""".format(self.transaction_no),
			as_dict=True,
		)
		# frappe.throw(frappe.as_json(data1))
		for row in data1:
			bank_name = frappe.db.get_value("Employee",row.employee,"bank_name")
			bank_ac_no = frappe.db.get_value("Employee",row.employee,"bank_ac_no")
			employee_name = frappe.db.get_value("Employee",row.employee,"employee_name")
			# frappe.throw(str(bank_ac_no))
			# beneficiary_name = frappe.db.get_value("Employee",row.employee,"bank_ac_no")


			row["bank_ac_no"] = bank_ac_no
			row["bank_name"] = bank_name
			row["employee_name"] = employee_name
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
			doc.transaction_code = "Intrabank transfer"
			doc.transaction_type = "Bulk DK Bank Payment"
			doc.paid_from = bulk_doc.paid_from
			doc.bank_account_no = bulk_doc.bank_account_no
			doc.transaction_no = bulk_doc.name

			doc.append("transaction", {
				"beneficiary_account_no": i.beneficiary_account_no,
				"beneficiary_name": i.beneficiary_name,
				"amount": i.amount,
				"bank_name": i.bank_name,
				"fx_rate": 1
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

			

