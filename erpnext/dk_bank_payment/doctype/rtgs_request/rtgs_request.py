# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RTGSRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data
		address: DF.Data | None
		amended_from: DF.Link | None
		amount_in_words: DF.Data | None
		amount_inr: DF.Currency
		bank_bank: DF.Data | None
		bene: DF.Data | None
		beneficiary_bank_address: DF.Data | None
		beneficiary_bank_swift_code: DF.Data | None
		beneficiary_name: DF.Data | None
		branch_name: DF.Data | None
		company: DF.Link
		date: DF.Date | None
		ifsc_code: DF.Data | None
		mobile_number: DF.Data | None
		name1: DF.Data | None
		name_of_the_account_holder: DF.Data
		posting_date: DF.Date | None
		purpose_of_remittance: DF.SmallText | None
		transaction: DF.DynamicLink | None
		transaction_type: DF.Link | None
		whom_to_mail: DF.Link
	# end: auto-generated types
	# pass
	def validate(self):
		self.send_notification()
	def on_submit(self):
		self.send_pdf_mail(self.name,self.doctype,self.whom_to_mail,"SWIFT Payment Instruction")

	def send_notification(self):
		state = self.workflow_state

		if state == "Waiting for Verification":
			send_to = frappe.db.get_value(
				"Company Notification Settings",
				{"name": self.company},
				"sp_verifier_email"
			)

			# frappe.throw(str(self.company))

			if not send_to:
				frappe.throw("Verifier email is not configured in Company Notification Settings")

			frappe.sendmail(
				recipients=[send_to],
				subject="Swift Payment Instruction Verification Needed",
				message=f"""
					Dear Sir/Madam,<br><br>
					You have a new RTGS Request<b>Pending Verification</b> with document no <b>{self.name}</b>.<br><br>
					Regards,<br>
					DK/GMC ERP System
				""",
			)

		elif state == "Waiting Approval":
			send_to = frappe.db.get_value(
				"Company Notification Settings",
				{"name": self.company},
				"sp_approver_email"
			)

			if not send_to:
				frappe.throw("Approver email is not configured in Company Notification Settings")

			frappe.sendmail(
				recipients=[send_to],
				subject="Swift Payment Instruction Approval Needed",
				message=f"""
					Dear Sir/Madam,<br><br>
					You have a new RTGS Request <b>Pending Approval</b> with document no <b>{self.name}</b>.<br><br>
					Regards,<br>
					DK/GMC ERP System
				""",
			)




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
				Regards,<br>GMC ERP
			""",
			attachments=[{
				"fname": filename,
				"fcontent": pdf_content
			}]
		)
