# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from erpnext.dk_integration_utils import intrabank_transfer,check_status_transaction,account_inquiry,fetch_exchange_rate
from frappe.utils import (
	flt,
	
)

class DKBankPayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.dk_bank_payment.doctype.dk_bank_payment_items.dk_bank_payment_items import DKBankPaymentItems
		from erpnext.epayment.doctype.dk_bank_payment_invoices.dk_bank_payment_invoices import DKBankPaymentInvoices
		from frappe.types import DF

		acc_status_details: DF.Data | None
		amended_from: DF.Link | None
		bank_account_no: DF.Data | None
		bank_balance: DF.Currency
		bank_balance_usd: DF.Float
		company: DF.Link | None
		in_queue: DF.Data | None
		inquiry_id: DF.Data | None
		invoice_number: DF.Data | None
		is_txn_processed: DF.Data | None
		paid_from: DF.Link | None
		party: DF.DynamicLink | None
		party_type: DF.Literal["Supplier", "Employee", "Customer"]
		payer_name: DF.Data | None
		posting_status_code: DF.Data | None
		remarks: DF.SmallText | None
		response_details: DF.Data | None
		table_eqqy: DF.Table[DKBankPaymentInvoices]
		transaction: DF.Table[DKBankPaymentItems]
		transaction_code: DF.Link
		transaction_id: DF.Data | None
		transaction_no: DF.DynamicLink | None
		transaction_status_request_id: DF.Data | None
		transaction_type: DF.Literal["Journal Entry", "Payment Entry", "Salary", "Bulk DK Bank Payment"]
		txn_authcode: DF.Data | None
		txn_drn: DF.Data | None
		txn_id: DF.Data | None
		txn_status_code: DF.Data | None
		txn_status_description: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.check_duplicate()
		self.send_notification()
		self.check_invoice_no()
		self.set_currency()

	def set_currency(self):
		for i in self.transaction:
			if self.transaction_code =='Intrabank transfer (USD-USD)':
				i.currency_code ="USD"
			else:
				i.currency_code ="BTN"

	def check_invoice_no(self):
		if self.invoice_number and self.party:
			exists = frappe.db.exists(
				"DK Bank Payment",
				{
					"invoice_number": self.invoice_number,
					"party": self.party,
					"name": ["!=", self.name]  # important for updates
				}
			)

			if exists:
				frappe.throw(
					"Invoice No {0} already exists for Party {1}"
					.format(self.invoice_number, self.party)
				)
		if self.table_eqqy:
			for i in self.table_eqqy:
				exists = frappe.db.sql('''
				select bpi.invoice as invoice, bp.name as doc_name  from `tabDK Bank Payment` bp inner join 
				`tabDK Bank Payment Invoices` bpi on bp.name=bpi.parent where 
				bp.party=%s 
				and bpi.invoice=%s and bp.name != %s;
				''',(self.party,i.invoice,self.name))

				if exists:
					frappe.throw("Invoice {} already exist for {}".format(exists[0][0],exists[0][1]))
					

	def check_duplicate(self):
		if self.transaction_type =='Bulk DK Bank Payment':
			return
		duplicate = frappe.db.exists(
			"DK Bank Payment",
			{
				"transaction_no": self.transaction_no,
				"name":["!=",self.name],
				"workflow_state": ["!=", "Failed"]
			}
			)
		# if duplicate:
		# 	frappe.throw("DK Bank Payment already exist for transaction {}".format(self.transaction_no))
	def on_submit(self):
		self.account_enquire()
		self.process_transaction()
		

	def send_notification(self):
		state = self.workflow_state

		if state == "Waiting for Verification":
			send_to = frappe.db.get_value(
				"Company Notification Settings",
				{"name": self.company},
				"verifier_email"
			)

			if not send_to:
				frappe.throw("Verifier email is not configured in Company Notification Settings")

			frappe.sendmail(
				recipients=[send_to],
				subject="DK Bank Payment Verification Needed",
				message=f"""
					Dear Sir/Madam,<br><br>
					You have a new DK Bank Payment <b>Pending Verification</b> with document no <b>{self.name}</b>.<br><br>
					Regards,<br>
					DK/GMC ERP System
				""",
			)

		elif state == "Waiting Approval":
			send_to = frappe.db.get_value(
				"Company Notification Settings",
				{"name": self.company},
				"approver_email"
			)

			if not send_to:
				frappe.throw("Approver email is not configured in Company Notification Settings")

			frappe.sendmail(
				recipients=[send_to],
				subject="DK Bank Payment Approval Needed",
				message=f"""
					Dear Sir/Madam,<br><br>
					You have a new DK Bank Payment <b>Pending Approval</b> with document no <b>{self.name}</b>.<br><br>
					Regards,<br>
					DK/GMC ERP System
				""",
			)
		
	def account_enquire(self):
		result = account_inquiry(self.bank_account_no)
		# frappe.throw(str(result))
		self.inquiry_id = result['response_data']['meta_info']['inquiry_id']
		# if self.transaction_code=="Intrabank transfer (USD-USD)":
		# 	frappe.throw('hi')
		# 	self.bank_balance = result['response_data']['balance_info']['usd_available_balance']
		# else:
		balance_info = result.get('response_data', {}).get('balance_info', {})

		if balance_info.get('btn_available_balance'):
			self.bank_balance = balance_info.get('btn_available_balance')

		if balance_info.get('usd_available_balance'):
			self.usd_bank_balance = balance_info.get('usd_available_balance')
		# if result['response_data']['balance_info']['btn_available_balance']:
		# 	self.bank_balance = result['response_data']['balance_info']['btn_available_balance']
		self.payer_name = result['response_data']['account_info']['account_name']
		self.payer_name = result['response_data']['account_info']['account_name']
		# frappe.throw(frappe.as_json(self.bank_balance))
		self.save()
		# frappe.db.commit()

	def process_transaction(self):
		response = intrabank_transfer(self)
		# response_code = response.get("response_code")
		# frappe.throw(frappe.as_json(response))
	
		# SUCCESS
		if not response['response_data']:
			frappe.throw(response['response_detail'])
		# frappe.throw(frappe.as_json(response))
		# if int(response['response_code']) == 5001:
		# 	frappe.throw(frappe.as_json(response['response_code']['response_data']))
		if int(response.get("response_code", 0)) == 5001:
			frappe.throw(frappe.as_json(response.get("response_data")))
		if int(response['response_data']['status']['status_code']) == 0:
			# frappe.throw(str(int(response['response_data']['status']['status_code'])))
			self.db_set("workflow_state", 'Completed')

		elif int(response['response_code']) == 4310:
			frappe.throw(response)
		# else:
		# 	if flt(response['response_data']['status']['status_code']) == 0:
		# 		self.db_set("workflow_state", 'Completed')
		# 	else:
		# 		self.db_set("workflow_state", 'Failed')
		# if	flt(response['response_code']) == 2004:
			# frappe.throw(str(response))
		# else:
		# 	self.db_set("workflow_state", 'Failed')
		# self.db_set("transaction_no", response["response_data"]["txn_id"])
		# self.db_set("transaction_status_request_id", response["response_data"]["txn_status_id"])
		self.db_set("response_details", response["response_data"]["status"]["status_code"])

		self.db_set("in_queue",response["response_data"]["in_queue"])
		self.db_set("is_txn_processed",response["response_data"]["status"]["is_txn_processed"])
		self.db_set("posting_status_code",response["response_data"]["status"]["status_code"])
		if "txn_auth_code" in response.get("response_data", {}).get("status", {}):
			self.db_set("txn_authcode", response["response_data"]["status"]["txn_auth_code"])
		self.db_set("txn_drn",response["response_data"]["status"]["txn_drn"])
		self.db_set("txn_id", response["response_data"]["txn_id"])
		self.db_set("txn_status_code",response["response_data"]["status"]["status_code"])
		self.db_set("txn_status_description",response["response_data"]['status']['status_description'])
		
		# self.db_set("")
		# dk_doc.in_queue = response["response_data"]["txn_status"]["in_queue"]
		# dk_doc.is_txn_processed = response["response_data"]["txn_status"]["is_txn_processed"]
		# dk_doc.posting_status_code = response["response_data"]["txn_status"]["posting_status_code"]
		# dk_doc.txn_authcode = response["response_data"]["txn_status"]["txn_auth_code"]
		# dk_doc.txn_drn = response["response_data"]["txn_status"]["txn_drn"]
		# dk_doc.txn_status_code = response["response_data"]["txn_status"]["txn_status_code"]
		# dk_doc.txn_status_description = response["response_data"]["txn_status"]["txn_status_description"]


	# def process_transaction(self):
	# 	response = intrabank_transfer(self)

	# 	if not response:
	# 		frappe.throw("No response received from intrabank transfer service.")

	# 	if response.get("response_code") == "4310":
	# 		frappe.throw(response.get("response_detail") or "Transaction failed with code 4310.")

	# 	response_data = response.get("response_data")
	# 	frappe.throw(str(response_data))
	# 	if not response_data or not response_data.get("meta_info"):
	# 		frappe.throw(f"Invalid response format: {response}")

	# 	meta_info = response_data["meta_info"]

	# 	self.db_set("transaction_id", meta_info.get("txn_id"))
	# 	self.db_set("transaction_status_request_id", meta_info.get("txn_status_req_id"))
	# 	self.db_set("response_details", response.get("response_detail"))

	@frappe.whitelist()
	def get_entries(self):
		self.load_items()

		return 1

	def load_items(self):
		total_amount = 0
		self.set("transaction", [])

		currency = frappe.db.sql("""
				SELECT currency 
				FROM `tabTransaction Code` 
				WHERE name= %s""",(self.transaction_code), as_dict=True)[0].currency
		if currency and currency.upper() != "BTN":
			result=fetch_exchange_rate(self.transaction_code)
			data = result.json()
			if data.get("response_code") != "0000":
				frappe.throw("Failed to fetch exchange rate: {}".format(
					data.get("response_detail", "No details provided")
				))

			rates = data.get("response_data", {}).get("exchange_rates", [])

			if not rates:
				frappe.throw("No exchange rate found")

			fx_rate = 1  # fallback

			for rate in rates:
				if rate.get("currency_code", "").upper() == currency.upper():
					fx_rate = float(rate.get("buy_rate", 1))
					break
		else:
			fx_rate = 1
				

		
		for i in self.get_transactions():
			if not i.beneficiary_name:
				frappe.throw("Please update beneficiary name in the supplier or employee")
			import re

			beneficiary_name = re.sub("[^A-Za-z0-9 ]+", "", i.beneficiary_name)
			row = self.append("transaction", {})
			row.currency_code = currency
			row.fx_rate = fx_rate

			
			row.update(i)
			# total_amount += flt(i.amount, 2)

	def get_transactions(self):
		data = []
		if self.transaction_type == "Salary":
			data = self.get_salary()
		elif self.transaction_type == "Journal Entry":
			data = self.get_journal_entry()
		elif self.transaction_type == "Payment Entry":
			data = self.get_payment_entry()
		
		
		return data
	
	def get_journal_entry(self):
		
		data = []
		cond = ""
		if self.transaction_no:
			cond = 'AND je.name = "{}"'.format(self.transaction_no)
		# elif not self.transaction_no and self.from_date and self.to_date:
		# 	cond = 'AND je.posting_date BETWEEN "{}" AND "{}"'.format(
		# 		str(self.from_date), str(self.to_date)
		# 	)
		data1= frappe.db.sql(
			"""SELECT je.name transaction_id, je.posting_date transaction_date, je.voucher_type,
								je.user_remark
								FROM `tabJournal Entry` je 
								where je.docstatus = 1
								{cond}
								AND je.voucher_type in ('Bank Entry','Contra Entry') 
								AND NOT EXISTS(select 1
									FROM `tabBank Payment Item` bpi
									WHERE bpi.transaction_type = 'Journal Entry'
									AND bpi.transaction_id = je.name
									AND bpi.parent != '{bank_payment}'
									AND bpi.docstatus != 2
									AND bpi.status NOT IN ('Cancelled', 'Failed')
								)
								ORDER BY je.posting_date
							""".format(
				bank_payment=self.name, cond=cond
			),
			as_dict=True,
		)
		
		for a in data1:
			if a.voucher_type == "Contra Entry":
				debit_amt = credit_amt = 0.00
				debit_bank_account = 0
				for p in frappe.db.sql(
					"""select a.account, round(a.debit_in_account_currency,2) as debit, 
									round(a.credit_in_account_currency,2) as credit,
									b.bank_name, b.bank_branch, b.bank_account_type, b.bank_ac_no, b.company
									from `tabJournal Entry Account` a
									inner join `tabAccount` b on a.account = b.name
									where a.parent = '{journal_entry}'
									and b.account_type = "Bank"
									""".format(
						journal_entry=a.transaction_id
					),
					as_dict=True,
				):
					debit_amt += p.debit
					credit_amt += p.credit
					if p.debit > 0:
						data.append(
							frappe._dict(
								{
									"transaction_type": "Journal Entry",
									"transaction_id": a.transaction_id,
									"transaction_date": a.transaction_date,
									"beneficiary_name": p.company,
									"bank_name": p.bank_name,
									"bank_branch": p.bank_branch,
									"bank_account_type": p.bank_account_type,
									"beneficiary_account_no": p.bank_ac_no,
									"amount": flt(p.debit),
									"status": "Draft",
								}
							)
						)
					if flt(p.debit) > 0:
						debit_bank_account += 1
			elif a.voucher_type == "Bank Entry":
				payment_dtl = []
				party_type = party = reference_type = reference_name = ""
				for b in frappe.db.sql(
					"""select party, party_type,
										sum(if(credit>0, credit, credit_in_account_currency)) as credit,
										sum(if(debit>0, debit, debit_in_account_currency)) as debit,
										sum(tax_amount) as tax_amount
									from `tabJournal Entry Account` 
									where parent = '{journal_entry}'
									AND party!="" AND party is NOT NULL
									group by party
								""".format(
						journal_entry=a.transaction_id
					),
					as_dict=True,
				):
					amount = flt(b.debit - b.credit - b.tax_amount, 2)
					payment_dtl.append(
						{
							"party": b.party,
							"party_type": b.party_type,
							"credit": b.credit,
							"debit": b.debit,
							"amount": amount,
						}
					)
				supplier, employee = None, None
				
				for i in payment_dtl:
					if i["party_type"] == "Supplier":
						query = """select s.bank_name, s.bank_branch, s.bank_account_type, 
										s.account_number as bank_account_no,s.account_holder_name as beneficiary_name,
										(CASE WHEN s.bank_name = "INR" THEN s.inr_bank_code ELSE NULL END) inr_bank_code,
										(CASE WHEN s.bank_name = "INR" THEN s.inr_purpose_code ELSE NULL END) inr_purpose_code
										from `tabSupplier` s
										WHERE s.name = '{party}'
									""".format(
							party=i["party"]
						)
						supplier = i["party"]
					elif i["party_type"] == "Employee":
						query = """select e.bank_name, e.bank_branch, e.bank_account_type, e.employee_name as beneficiary_name,
										e.bank_ac_no as bank_account_no, NULL inr_bank_code, NULL inr_purpose_code
										from `tabEmployee` e
										WHERE e.name = '{party}'
									""".format(
							party=i["party"]
						)
						employee = i["party"]
					elif i["party_type"] == "Muster Roll Employee":
						query = """select e.bank_name, e.bank_branch, e.bank_account_type, e.person_name as beneficiary_name,
										e.bank_ac_no as bank_account_no, NULL inr_bank_code, NULL inr_purpose_code
										from `tabMuster Roll Employee` e
										WHERE e.name = '{party}'
									""".format(
							party=i["party"]
						)
					dtl = frappe.db.sql(query, as_dict=True)
					
					data.append(
						frappe._dict(
							{
								
								
								"employee": employee,
								"supplier": supplier,
								"beneficiary_name": dtl[0]["beneficiary_name"],
								"bank_name": dtl[0]["bank_name"],
								# "currency_code": "USD" if self.transaction_code == "Intrabank transfer (USD-USD)" else "BTN",
								"currency_code": "BTN",
								"beneficiary_account_no": dtl[0]["bank_account_no"],
								"amount": flt(i["amount"]),
								
							}
						)
					)

			# frappe.throw(frappe.as_json(data))
		return data
	
	def get_payment_entry(self):
		cond = ""
		if self.transaction_no:
			
			cond = 'where pe.name = "{}"'.format(self.transaction_no)
			
		# elif not self.transaction_no and self.from_date and self.to_date:
		# 	cond = 'AND pe.posting_date BETWEEN "{}" AND "{}"'.format(
		# 		str(self.from_date), str(self.to_date)
		# 	)
		
		return frappe.db.sql(
						"""SELECT  
				pe.party AS supplier,
				s.account_holder_name AS beneficiary_name, 
				"BTN" as currency_code,
				s.bank_name AS bank_name,
				s.account_number AS beneficiary_account_no,
				ROUND((
					pe.paid_amount_after_tax +
					(
						SELECT IFNULL(SUM(ped.amount), 0)
						FROM `tabPayment Entry Deduction` ped
						WHERE ped.parent = pe.name
					)
				), 2) AS amount
			FROM `tabPayment Entry` pe
			JOIN `tabSupplier` s ON s.name = pe.party
			LEFT JOIN `tabBank` fib ON fib.name = s.bank_name
			{cond}
			AND pe.docstatus = 1
			AND pe.party_type = 'Supplier'
			AND pe.party IS NOT NULL
			AND IFNULL(pe.paid_amount, 0) > 0
			AND NOT EXISTS (
				SELECT 1
				FROM `tabBank Payment Item` bpi
				WHERE bpi.transaction_type = 'Payment Entry'
				AND bpi.transaction_id = pe.name
				AND bpi.parent != '{bank_payment}'
							AND bpi.docstatus != 2
							AND bpi.status NOT IN ('Cancelled', 'Failed')
						)
						ORDER BY pe.posting_date, pe.name
			""".format(
							bank_payment=self.name,  cond=cond
						),
						as_dict=True,
					)

@frappe.whitelist()

def get_currency_code(company):
	return frappe.db.get_value("Company", company, "default_currency")

@frappe.whitelist()
def check_transaction_status(doc):
	# data = frappe.as_json(doc)
	data = json.loads(doc)
	# frappe.throw(str(data['name']))
	# Fetch the document using the correct doctype name
	dk_doc = frappe.get_doc("DK Bank Payment", str(data['name']))

	# Call your function to get transaction status
	response = check_status_transaction(doc)
	# frappe.throw(str(response))
	
	# frappe.throw(frappe.as_json(response))
	# Update the 'in_queue' field
	# dk_doc.in_queue = response.get("txn_status_info", {}).get("in_queue")
	dk_doc.in_queue = response["response_data"]["txn_status"]["in_queue"]
	dk_doc.is_txn_processed = response["response_data"]["txn_status"]["is_txn_processed"]
	dk_doc.posting_status_code = response["response_data"]["txn_status"]["posting_status_code"]
	dk_doc.txn_authcode = response["response_data"]["txn_status"]["txn_auth_code"]
	dk_doc.txn_drn = response["response_data"]["txn_status"]["txn_drn"]
	dk_doc.txn_status_code = response["response_data"]["txn_status"]["txn_status_code"]
	dk_doc.txn_status_description = response["response_data"]["txn_status"]["txn_status_description"]
	

	# frappe.throw(str(dk_doc.in_queue))

	# Save and commit
	dk_doc.save()

	if float(response["response_data"]["txn_status"]["txn_status_code"]) == 0:
		frappe.db.sql('''
			update `tabDK Bank Payment` set workflow_state='Completed' where name='{}'
		'''.format(dk_doc.name))
	elif float(response["response_data"]["txn_status"]["txn_status_code"]) == 51:
		frappe.db.sql('''
			update `tabDK Bank Payment` set workflow_state='Failed' where name='{}'
		'''.format(dk_doc.name))
	elif float(response["response_code"]) == 3001:
		frappe.db.sql('''
			update `tabDK Bank Payment` set workflow_state='Failed' where name='{}'
		'''.format(dk_doc.name))
	frappe.db.commit()
	return 1