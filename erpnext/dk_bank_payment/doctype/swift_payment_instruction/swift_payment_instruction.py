# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.pdf import get_pdf
from frappe import sendmail, get_doc


class SWIFTPaymentInstruction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data | None
		account_source: DF.Data | None
		amended_from: DF.Link | None
		amount_in_usd: DF.Data | None
		amount_in_word: DF.Data | None
		bank_application_remittance_reference_number: DF.Data | None
		beneficiary_account_no: DF.Data | None
		beneficiary_address: DF.Data | None
		beneficiary_bank_address: DF.Data | None
		beneficiary_bank_name: DF.Data | None
		beneficiary_bank_swift_code: DF.Data | None
		beneficiary_name: DF.Data | None
		btfn_application_reference_number: DF.Data | None
		charges_currency: DF.Literal["USD", "BTN"]
		charges_to_debited_from: DF.Literal["Our", "Beneficiary", "Share"]
		commission_debit_account_number: DF.Data | None
		company: DF.Data | None
		customer_declaration_number: DF.Data | None
		email: DF.Data | None
		form_data: DF.Data | None
		intermediary_bank_address: DF.Data | None
		intermediary_bank_name: DF.Data | None
		intermediary_bank_swift_code: DF.Data | None
		name1: DF.Data | None
		national_id: DF.Data | None
		permanent_address: DF.Data | None
		phone_number: DF.Data | None
		posting_date: DF.Date | None
		present_address: DF.Data | None
		reason: DF.Data | None
		transaction_id: DF.DynamicLink | None
		transaction_type: DF.Literal["", "Journal Entry", "Payment Entry"]
		type_of_payment: DF.Literal["Advance Payment", "Partial Payment", "Final Payment"]
		whom_to_mail: DF.Data | None
		workflow_state: DF.Data | None
	# end: auto-generated types
	def on_submit(self):
		self.send_pdf_mail(self.name,self.doctype,self.whom_to_mail,"SWIFT Payment Instruction")

	def send_pdf_mail(self,docname, doctype, recipient_email, print_format):
    # Get the document
		doc = get_doc(doctype, docname)

		# Generate PDF with the specified print format
		pdf_content = get_pdf(frappe.get_print(doctype, docname, print_format=print_format))

		# Define the filename
		filename = f"{doctype}-{docname}.pdf"

		# Send email
		sendmail(
			recipients=[recipient_email],
			subject=f"{doctype} {docname} - PDF Attachment",
			message=f"""
				Dear Customer,<br><br>
				Please find attached the {doctype.lower()} document: <b>{docname}</b>.<br><br>
				Regards,<br>Your Company
			""",
			attachments=[{
				"fname": filename,
				"fcontent": pdf_content
			}]
		)
	@frappe.whitelist()
	def get_entries(self):
		credit_data = frappe.db.sql('''
			SELECT party, debit
			FROM `tabJournal Entry Account` 
			WHERE parent = %s and debit>0
		''', (self.transaction_id,), as_dict=True)

		debit_data = frappe.db.sql('''
			SELECT account
			FROM `tabJournal Entry Account` 
			WHERE parent = %s and credit>0
		''', (self.transaction_id,), as_dict=True)
		
		if credit_data:
			self.name1 = credit_data[0]['party']
			self.amount_in_usd =credit_data[0]['debit']

		party = credit_data[0]['party']

		if debit_data:
			bank_data = frappe.db.sql('''
			SELECT bank_ac_no
			FROM `tabAccount` 
			WHERE name = %s 
		''', (debit_data[0]['account'],), as_dict=True)

		if bank_data:
			self.account_number = bank_data[0]['bank_ac_no']

		supplier_info = frappe.db.sql('''
			SELECT telephone_and_fax, country, location,email_address,national_id,
			bank, bank_address, swift_account_holder_name,bank_address,swift_code,
			acc_no_swift
			FROM `tabSupplier`
			WHERE name = %s
		''', (party,), as_dict=True)

		if supplier_info:
			self.phone_number = supplier_info[0]['telephone_and_fax']
			self.present_address = supplier_info[0]['location']
			self.email = supplier_info[0]['email_address']
			self.national_id = supplier_info[0]['national_id']
			self.beneficiary_bank_name = supplier_info[0]['bank']
			self.beneficiary_name = supplier_info[0]['swift_account_holder_name']
			self.beneficiary_bank_address = supplier_info[0]['bank_address']
			self.beneficiary_bank_swift_code = supplier_info[0]['swift_code']
			self.beneficiary_address = supplier_info[0]['location']
			self.beneficiary_account_no = supplier_info[0]['acc_no_swift']
		return 1
		# frappe.throw(str(data))
		
		
		
