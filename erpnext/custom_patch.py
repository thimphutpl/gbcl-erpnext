import frappe

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
	