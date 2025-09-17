import frappe
from erpnext.dk_integration_utils import fetch_fx_rate
def make_journal_entry():
	doc = frappe.get_doc("Employee Advance", "HR-EAD-2025-00004")
	doc.post_journal_entry()
	print("DONE")

def change_acc_abbr():
	acc = frappe.db.sql('''
		select name from `tabAccount` where company="Digital Kidu";
	''',as_dict=True)
	for i in acc:
		print(str(i['name']))
		# frappe.db.set_value('Account',acc)
def change_acc_abbr():
	acc_list = frappe.db.sql('''
		SELECT name FROM `tabAccount` WHERE company="DK Oro"
	''', as_dict=True)

	for acc in acc_list:
		old_name = acc['name']
		if old_name.endswith(' - d'):
			# new_name = old_name.replace(' - DB', ' - DK')
			new_name = old_name.replace(' - d', ' - Oro')
			print(f"Renaming: {old_name} -> {new_name}")
			# Rename the account
			frappe.rename_doc('Account', old_name, new_name, force=True)
			 # Stop after first rename
			# break

	frappe.db.commit()

def post_fx_rate():
	try:
		response = fetch_fx_rate().json()
		
		
		

		for i in response['response_data']['exchange_rates']:
			currency_code = i['currency_code']
			if i['currency_code'] == "EURO":
				currency_code= "EUR"
			from_currency = currency_code
			to_currency = 'BTN'
			rate = i['buy_rate']
			effect_date = i['effect_date']

			# Check for existing entry
			exists = frappe.db.exists("Currency Exchange", {
				"from_currency": from_currency,
				"to_currency": to_currency,
				"date": effect_date
			})

			if exists:
				frappe.logger().info(f"Skipped: {from_currency} to {to_currency} on {effect_date} already exists.")
				continue

			# Create new exchange entry
			exchange = frappe.new_doc("Currency Exchange")
			exchange.from_currency = from_currency
			exchange.to_currency = to_currency
			exchange.exchange_rate = rate
			exchange.date = effect_date

			exchange.insert()
			exchange.submit()

		frappe.logger().info("Currency Exchange import completed.")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Currency Exchange Import Failed")

		

# def enque_fx_rate():
# 	enqueue(post_fx_rate)
# from erpnext.cbs_gl_import.doctype.gl_turnover_entry.gl_turnover_entry import handle_glturnover_oro
# def post_gl_turn_over(currency):
# 	gl_turn_over = frappe.new_doc('GL Turnover Entry')
# 	gl_turn_over.company='Oro Bank'
# 	gl_turn_over.currency=currency
# 	gl_turn_over.cost_center='Finance and Treasury - OB'
# 	gl_turn_over.branch='Finance & Treasury (ORO)'
# 	gl_turn_over.date = frappe.utils.today()
# 	gl_turn_over.save()

# 	handle_glturnover_oro(gl_turn_over.date,gl_turn_over.name,gl_turn_over.currency)
# 	gl_turn_over.reload()
# 	gl_turn_over.submit()

# def bulk_post_gl_turn_over():
#     currencies = ['USD', 'SING', 'HKD', 'GBP', 'AUD', 'EUR']
#     for currency in currencies:
#         post_gl_turn_over(currency)

	
from erpnext.cbs_gl_import.doctype.gl_turnover_entry.gl_turnover_entry import handle_glturnover_oro

import frappe
import logging

logger = logging.getLogger(__name__)

def post_gl_turn_over(currency):
	try:
		gl_turn_over = frappe.new_doc('GL Turnover Entry')
		gl_turn_over.company = 'Oro Bank'
		gl_turn_over.currency = currency
		gl_turn_over.cost_center = 'Finance and Treasury - OB'
		gl_turn_over.branch = 'Finance & Treasury (ORO)'
		gl_turn_over.date = frappe.utils.today()
		gl_turn_over.save()

		# handle missing data gracefully
		try:
			handle_glturnover_oro(gl_turn_over.date, gl_turn_over.name, gl_turn_over.currency)
		except Exception as e:
			logger.warning(f"No data for {currency} on {gl_turn_over.date}: {str(e)}")
			# continue without submitting
			gl_turn_over.delete()
			return

		gl_turn_over.reload()
		gl_turn_over.submit()
		frappe.db.commit()
		logger.info(f"Posted turnover for {currency}")

	except frappe.ValidationError as e:
		logger.warning(f"Skipping {currency}: {str(e)}")
		logger.warning(f"No data for {currency} on {gl_turn_over.date}: {str(e)}")
		frappe.db.rollback()

	except Exception as e:
		logger.error(f"Unexpected error for {currency}: {frappe.get_traceback()}")
		frappe.db.rollback()


def bulk_post_gl_turn_over():
	currencies = ['USD', 'AUD', 'HKD', 'GBP', 'SGD', 'EUR']
	for currency in currencies:
		post_gl_turn_over(currency)

import frappe
from frappe.utils.password import update_password

# Example: set password for one user
# update_password("user@example.com", "Test@123")

# Example: set the same password for all system users

def setPass():
	for user in frappe.get_all("User", filters={"enabled": 1}, pluck="name"):
		if user not in ("Administrator", "Guest"):  # skip system users
			update_password(user, "GMC@123")
			print(f"Password updated for {user}")
