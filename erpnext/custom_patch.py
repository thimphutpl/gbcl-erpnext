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
	