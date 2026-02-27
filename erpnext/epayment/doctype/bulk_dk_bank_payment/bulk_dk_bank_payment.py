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
		frappe.enqueue(
			method="erpnext.epayment.doctype.bulk_dk_bank_payment.bulk_dk_bank_payment.create_bank_payments",
			queue="long",
			timeout=600,
			bulk_doc_name=self.name
		)

# def create_bank_payments(bulk_doc_name):
# 	bulk_doc = frappe.get_doc("Bulk DK Bank Payment", bulk_doc_name)
# 	created_payments = []

# 	for row in bulk_doc.transaction:
# 		# if row.dk_bank_payment:
# 		# 	continue

# 		try:
# 			doc = frappe.new_doc("DK Bank Payment")
			
# 			# Set all fields
# 			doc.company = bulk_doc.company
# 			doc.transaction_code = "Intrabank transfer"
# 			doc.transaction_type = "Bulk DK Bank Payment"
# 			doc.paid_from = bulk_doc.paid_from
# 			doc.bank_account_no = bulk_doc.bank_account_no
# 			doc.transaction_no = bulk_doc.name

# 			doc.append("transaction", {
# 				"beneficiary_account_no": row.beneficiary_account_no,
# 				"beneficiary_name": row.beneficiary_name,
# 				"amount": row.amount,
# 				"bank_name": row.bank_name
# 			})

# 			# CRITICAL FIX: Use a more unique naming series
# 			# Option A: Set explicit name with timestamp + random
# 			import random
# 			import string
# 			timestamp = frappe.utils.now_datetime().strftime("%Y%m%d%H%M%S")
# 			random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
# 			doc.name = f"DKBP-{timestamp}-{random_suffix}"
			
# 			# Option B: Or set flags to retry on duplicate
# 			doc.flags.ignore_permissions = True
# 			doc.flags.ignore_links = True
			
# 			doc.account_enquire()
			
# 			# Try with retry mechanism
# 			max_retries = 3
# 			for attempt in range(max_retries):
# 				try:
# 					doc.insert(ignore_permissions=True, ignore_if_duplicate=False)
# 					break
# 				except frappe.DuplicateEntryError:
# 					if attempt == max_retries - 1:
# 						raise
# 					# Generate new name and retry
# 					new_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
# 					doc.name = f"DKBP-{timestamp}-{new_suffix}"
# 					continue

# 			frappe.db.commit()
			
# 			# Link back to child row
# 			frappe.db.set_value("Bulk DK Bank Payment Item", row.name, "dk_bank_payment", doc.name)
# 			created_payments.append(doc.name)

# 		except Exception as e:
# 			frappe.log_error(
# 				title="Bulk DK Bank Payment Error",
# 				message=frappe.get_traceback()
# 			)
# 			frappe.db.rollback()
# 			# Don't raise immediately, try other rows
# 			continue

# 	return created_payments


	# def on_submit(self):
	# 	# Check if any payments already exist
	# 	existing_payments = [row for row in self.transaction if row.dk_bank_payment]
	# 	if existing_payments:
	# 		frappe.throw("Some transactions already have linked payments. Please clear them first.")
		
	# 	# Process each transaction
	# 	for row in self.transaction:
	# 		try:
	# 			doc = frappe.new_doc("DK Bank Payment")
	# 			doc.company = self.company
	# 			doc.transaction_code = "Intrabank transfer"
	# 			doc.transaction_type = "Bulk DK Bank Payment"
	# 			doc.paid_from = self.paid_from
	# 			doc.bank_account_no = self.bank_account_no
	# 			doc.transaction_no = self.name

	# 			# Fixed duplicate keys
	# 			doc.append("transaction", {
	# 				"beneficiary_account_no": row.beneficiary_account_no,
	# 				"beneficiary_name": row.beneficiary_name,
	# 				"amount": row.amount,
	# 				"bank_name": row.bank_name
	# 			})

	# 			doc.account_enquire()
	# 			doc.insert(ignore_permissions=True)
				
	# 			# Link back to child row
	# 			frappe.db.set_value("Bulk DK Bank Payment Item", row.name, "dk_bank_payment", doc.name)
				
	# 		except Exception as e:
	# 			frappe.log_error(
	# 				title="Bulk DK Bank Payment Error",
	# 				message=frappe.get_traceback()
	# 			)
	# 			frappe.throw("Error creating payment for row {0}: {1}").format(row.idx, str(e))

	# 	frappe.db.commit()

	# end: auto-generated types
	# def on_submit(self):
	# 	for i in self.transaction:
	# 		doc = frappe.new_doc("DK Bank Payment")
	# 		doc.company = self.company
	# 		doc.transaction_code = 'Intrabank transfer'
	# 		doc.transaction_type = 'Bulk DK Bank Payment'
	# 		doc.paid_from = self.paid_from
	# 		doc.bank_account_no = self.bank_account_no
	# 		doc.transaction_no = self.name

	# 		doc.append("transaction", {
	# 			"beneficiary_account_no": i.beneficiary_account_no,
	# 			"bank_name": i.bank_name
	# 		})

	# 		doc.account_enquire()

	# 		doc.insert(ignore_permissions=True)

		# def on_submit(self):
		# 	# frappe.enqueue(
		# 	# method="erpnext.epayment.doctype.bulk_dk_bank_payment.bulk_dk_bank_payment.create_bank_payments",
		# 	# queue="long",
		# 	# timeout=600,
		# 	# bulk_doc_name=self.name
		# 	# )


		# 	for i in self.transaction:
		# 		doc = frappe.new_doc("DK Bank Payment")
		# 		doc.company = self.company
		# 		doc.transaction_code= 'Intrabank transfer'
		# 		doc.transaction_type ='Bulk DK Bank Payment'
		# 		doc.paid_from = self.paid_from
		# 		doc.bank_account_no = self.bank_account_no
		# 		doc.transaction_no = self.name

		# 		# doc.append("transaction", {
		# 		# 	"beneficiary_account_no": i.beneficiary_account_no,
		# 		# 	"bank_name": i.bank_name
		# 		# })
		# 		doc.append("transaction", {
		# 			"beneficiary_account_no": i.beneficiary_account_no,
		# 			"beneficiary_name":i.beneficiary_name,
		# 			"amount":i.amount,
		# 			"bank_name": i.bank_name,
		# 			"beneficiary_name":i.beneficiary_name,
		# 			"amount":i.amount
		# 		})

		# 		doc.account_enquire()
		# 		doc.insert()
		# 		frappe.db.commit()
# def create_bank_payments(bulk_doc_name):
# 	bulk_doc = frappe.get_doc("Bulk DK Bank Payment", bulk_doc_name)
# 	created_payments = []

# 	for i in bulk_doc.transaction:
# 		# Skip if already processed
# 		# if i.dk_bank_payment:
# 		# 	continue

# 		try:
# 			doc = frappe.new_doc("DK Bank Payment")
# 			doc.company = bulk_doc.company
# 			doc.transaction_code = 'Intrabank transfer'
# 			doc.transaction_type = 'Bulk DK Bank Payment'
# 			doc.paid_from = bulk_doc.paid_from
# 			doc.bank_account_no = bulk_doc.bank_account_no
# 			doc.transaction_no = bulk_doc.name

# 			doc.append("transaction", {
# 				"beneficiary_account_no": i.beneficiary_account_no,
# 				"beneficiary_name":i.beneficiary_name,
# 				"amount":i.amount,
# 				"bank_name": i.bank_name,
# 				"beneficiary_name":i.beneficiary_name,
# 				"amount":i.amount
# 			})

# 			doc.account_enquire()
# 			doc.insert(ignore_permissions=True)

# 			frappe.db.commit()
			
# 		except Exception as e:
# 			frappe.log_error(f"Error creating payment for {i.name}: {str(e)}")
# 			frappe.db.rollback()
# 			raise

		
# 	return created_payments
def create_bank_payments(bulk_doc_name):
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
				"bank_name": i.bank_name
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

