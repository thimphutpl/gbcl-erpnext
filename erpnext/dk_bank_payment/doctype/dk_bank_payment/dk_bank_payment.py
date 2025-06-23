# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.dk_integration_utils import intrabank_transfer,check_status_transaction

class DKBankPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.dk_bank_payment.doctype.dk_bank_payment_items.dk_bank_payment_items import DKBankPaymentItems
		from frappe.types import DF

		acc_status_details: DF.Data | None
		amended_from: DF.Link | None
		bank_account_no: DF.Data | None
		bank_balance: DF.Currency
		bank_balance_usd: DF.Currency
		company: DF.Link | None
		in_queue: DF.Data | None
		inquiry_id: DF.Data | None
		is_txn_processed: DF.Data | None
		payer_name: DF.Data | None
		posting_status_code: DF.Data | None
		remarks: DF.SmallText | None
		response_details: DF.Data | None
		transaction: DF.Table[DKBankPaymentItems]
		transaction_id: DF.Data | None
		transaction_status_request_id: DF.Data | None
		transaction_type: DF.Literal["Journal Entry", "Salary"]
		txn_authcode: DF.Data | None
		txn_drn: DF.Data | None
		txn_status_code: DF.Data | None
		txn_status_description: DF.Data | None
	# end: auto-generated types
	def on_submit(self):
		self.process_transaction()
		
		
	def process_transaction(self):
		response = intrabank_transfer(self)
		self.db_set("transaction_id", response["response_data"]["meta_info"]["txn_id"])
		self.db_set("transaction_status_request_id", response["response_data"]["meta_info"]["txn_status_req_id"])
		self.db_set("response_details", response["response_detail"])

import json

@frappe.whitelist()
def check_transaction_status(doc):
	# data = frappe.as_json(doc)
	data = json.loads(doc)
	# frappe.throw(str(data['name']))
	# Fetch the document using the correct doctype name
	dk_doc = frappe.get_doc("DK Bank Payment", str(data['name']))

	# Call your function to get transaction status
	response = check_status_transaction(doc)
	
	# frappe.throw(frappe.as_json(response))
	# Update the 'in_queue' field
	# dk_doc.in_queue = response.get("txn_status_info", {}).get("in_queue")
	dk_doc.in_queue = response["response_data"]["txn_status_info"]["in_queue"]
	dk_doc.is_txn_processed = response["response_data"]["txn_status_info"]["is_txn_processed"]
	dk_doc.posting_status_code = response["response_data"]["txn_status_info"]["posting_status_code"]
	dk_doc.txn_authcode = response["response_data"]["txn_status_info"]["txn_authcode"]
	dk_doc.txn_drn = response["response_data"]["txn_status_info"]["txn_drn"]
	dk_doc.txn_status_code = response["response_data"]["txn_status_info"]["txn_status_code"]
	dk_doc.txn_status_description = response["response_data"]["txn_status_info"]["txn_status_description"]
	# dk_doc.workflow_state = "Completed"

	# frappe.throw(str(dk_doc.in_queue))

	# Save and commit
	dk_doc.save()
	frappe.db.commit()
	return 1