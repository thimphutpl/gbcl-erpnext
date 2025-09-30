# # Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.utils import flt, getdate, formatdate, cstr, rounded
# from erpnext.accounts.report.financial_statements \
# 	import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows

# def execute(filters=None):
# 	columns = get_columns()
# 	data = get_accounts(filters)
# 	return columns, data

# def get_accounts(filters):
# 	company = filters.get("company")
# 	data = []
# 	for a in frappe.db.sql("""SELECT a.name, b.fixed_asset_account as fa, b.accumulated_depreciation_account as acc, 
# 								b.depreciation_expense_account as dep from `tabAsset Category` a, 
# 							`tabAsset Category Account` b 
# 							where a.name = b.parent and a.company = %s""", 
# 							company, as_dict=True):
# 		gross_opening = get_values(a.fa, filters.to_date, filters.from_date, filters.cost_center, company, opening=True)[0]
# 		gross = get_values(a.fa, filters.to_date, filters.from_date, filters.cost_center, company)[0]
# 		dep_opening = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center, company, opening=True)[0]
# 		acc_dep = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center, company)[0]
# 		# following line commented by SHIV on 2021/03/10 as it is not used anywhere
# 		#dep = get_values(a.dep, filters.to_date, filters.from_date, filters.cost_center, company)[0]
# 		adj = get_values(a.acc, filters.to_date, filters.from_date, filters.cost_center, company, adjustment=True)[0]		

# 		g_open = flt(gross_opening.debit) - flt(gross_opening.credit)
# 		g_addition = flt(gross.debit)
# 		g_adjustment = flt(gross.credit)
# 		g_total = g_open + g_addition - g_adjustment
# 		#frappe.msgprint(str(dep_opening.debit)+" "+str(dep_opening.credit))
# 		d_open = -1 * (flt(dep_opening.debit) - flt(dep_opening.credit))
# 		dep_adjust = flt(acc_dep.debit)
# 		adj_adjust = flt(adj.credit)
# 		dep_addition = flt(acc_dep.credit) - flt(adj.credit)
# 		dep_add = flt(acc_dep.credit)
# 		d_total = d_open + dep_add  - flt(dep_adjust)
		
# 		income_tax = frappe.db.sql("""select  sum(b.income_depreciation_amount) as total_income_tax
# 										from `tabAsset` a, `tabDepreciation Schedule` b, `tabAsset Depreciation Schedule` ads
# 										where ads.name = b.parent
# 											and ads.asset = a.name
# 											and a.asset_category = %s
# 											and a.company = %s
# 											and b.schedule_date between %s and CURDATE()
# 											and a.docstatus = 1
# 											and (
# 												a.status not in ('Scrapped', 'Sold')
# 												OR
# 												(a.status in ('Scrapped', 'Sold') AND a.disposal_date >= %s)
# 											)
# 									""", (a.name, company, filters.from_date, filters.from_date), as_dict=True)

# 		opening_it_dep = frappe.db.sql("""select 
# 												sum(b.income_accumulated_depreciation) as acc_income_tax,
# 												sum(b.income_depreciation_amount) as depreciation_income_tax
# 							   			from `tabAsset` a, `tabDepreciation Schedule` b, `tabAsset Depreciation Schedule` ads
# 						 	 			where ads.name = b.parent
# 											and ads.asset = a.name
# 						  					and a.asset_category = %s
# 						  					and a.company = %s
# 						  					and (%s between b.schedule_start_date and b.schedule_date
# 												or 
# 												(b.schedule_date < %s 
# 													and 
# 												b.schedule_date = (select max(c.schedule_date) 
# 																	from `tabDepreciation Schedule` c
# 																	where c.parent = ads.name)
# 												))
# 											and a.docstatus = 1
# 											and (
# 												a.status not in ('Scrapped', 'Sold')
# 												OR
# 												(a.status in ('Scrapped', 'Sold') AND a.disposal_date >= %s)
# 											)
# 									""", (a.name, company, filters.from_date, filters.from_date, filters.from_date), as_dict=True)

# 		opening_dep = frappe.db.sql("""select  sum(a.income_tax_opening_depreciation_amount) as it_opening
# 										from `tabAsset` a
# 						 	 			where a.asset_category = %s
# 						  					and a.company = %s
# 						  					and a.docstatus = 1
# 											and (
# 												a.status not in ('Scrapped', 'Sold')
# 												OR
# 												(a.status in ('Scrapped', 'Sold') AND a.disposal_date >= %s)
# 											)
# 											and NOT EXISTS(
# 												select 1
# 												from  `tabDepreciation Schedule` b, `tabAsset Depreciation Schedule` ads
# 												where ads.asset = a.name and b.parent = ads.name
# 											)	
# 								""", (a.name, company, filters.from_date), as_dict=True)
# 		acc_it = opening_it_dep[0].acc_income_tax if opening_it_dep[0].acc_income_tax else 0.00
# 		depreciation_it = opening_it_dep[0].depreciation_income_tax if opening_it_dep[0].depreciation_income_tax else 0.00
# 		it_opening = opening_dep[0].it_opening if opening_dep[0].it_opening else 0.00
		
# 		data.append({
# 			"company": company,
# 			"asset_category": a.name,
# 			"gross_opening":g_open,
# 			"gross_addition":g_addition,
# 			"gross_adjustment":g_adjustment,
# 			"gross_total":g_total,
# 			"dep_opening":d_open,
# 			"dep_addition":dep_addition,
# 			"dep_adjustment":dep_adjust,
# 			"dep_total":d_total,
# 			"net_block":flt(g_total) - flt(d_total),
# 			"opening_income_tax":acc_it - depreciation_it + it_opening,
# 			"it_dep_addition":income_tax[0].total_income_tax
# 		})

# 	#For CWIP Account
# 	if flt(filters.include_cwip):
# 		row = get_cwip(filters)
# 		data.append(row)
# 	return data

# def get_cwip(filters):
# 	company = filters.get("company")
# 	cwip_acc = []
# 	cwip_account = frappe.db.get_value("Company", company, "capital_work_in_progress_account")
# 	if not cwip_account:
# 		frappe.throw("Capital Work In Progress Account is missing. Please set CWIP account in Company Setting")
# 	cwip_accounts_gl = frappe.db.sql("select name from tabAccount where parent_account = %s and company = %s", (cwip_account, company), as_dict=True)
# 	for account in cwip_accounts_gl:
# 		cwip_acc.append(str(account.name))
# 	cwip_accounts = tuple(cwip_acc)

# 	cwip_open = get_values(cwip_accounts, filters.to_date, filters.from_date, filters.cost_center, company, opening=True, cwip=True)
# 	cwip = get_values(cwip_accounts, filters.to_date, filters.from_date, filters.cost_center, company, cwip=True)

# 	cwip_open = cwip_open[0]
# 	cwip = cwip[0]

# 	c_open = flt(cwip_open.debit) - flt(cwip_open.credit)
# 	c_total = c_open + flt(cwip.debit) - flt(cwip.credit)

# 	row = {
# 		"company": company,
# 		"asset_category": "Capital Work in Progress",
# 		"gross_opening":c_open,
# 		"gross_addition":cwip.debit,
# 		"gross_adjustment":cwip.credit,
# 		"gross_total":c_total,
# 		"dep_opening":0,
# 		"dep_addition":0,
# 		"dep_adjustment":0,
# 		"dep_total":0,
# 		"net_block":0,
# 		"opening_income_tax":c_total,
# 		"it_dep_addition":0
# 	}
# 	return row

# def get_values(account, to_date, from_date, cost_center=None, company=None, opening=False, cwip=False, adjustment=False):
# 	if cwip:
# 		query = """select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` 
# 			where account in %s and docstatus = 1 and is_cancelled = 0 and company = %s"""
# 		params = [account, company]
# 	elif adjustment:
# 		return [frappe._dict({"debit": 0.0, "credit": 0.0})]
# 	else:
# 		query = """select sum(debit) as debit, sum(credit) as credit from `tabGL Entry` 
# 			where account = %s and docstatus = 1 and is_cancelled = 0 and company = %s"""
# 		params = [account, company]
		
# 	if not opening:
# 		query += " and posting_date between %s and %s"
# 		params.extend([from_date, to_date])
# 	else:
# 		query += " and posting_date < %s"
# 		params.append(from_date)
		
# 	if cost_center:
# 		query += " and cost_center = %s"
# 		params.append(cost_center)

# 	query += " and voucher_type not in ('Period Closing Voucher', 'Asset Movement', 'Bulk Asset Transfer')"
	
# 	value = frappe.db.sql(query, tuple(params), as_dict=True)

# 	return value


# def get_columns():
# 	return [
# 		{
# 			"fieldname": "company",
# 			"label": _("Company"),
# 			"fieldtype": "Link",
# 			"options": "Company",
# 			"width": 200
# 		},
# 		{
# 			"fieldname": "asset_category",
# 			"label": _("Asset Category"),
# 			"fieldtype": "Data",
# 			"width": 200
# 		},
# 		{
# 			"fieldname": "gross_opening",
# 			"label": _("Opening Acquisation"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "gross_addition",
# 			"label": _("Acquisation During the Year"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "gross_adjustment",
# 			"label": _("Adjustment During the Year"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "gross_total",
# 			"label": _("Gross Total"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "dep_opening",
# 			"label": _("Accumulated Dep."),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "dep_addition",
# 			"label": _("Dep. During the Year"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "dep_adjustment",
# 			"label": _("Dep. Adjustment During the Year"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "dep_total",
# 			"label": _("Dep. Total"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "net_block",
# 			"label": _("Net Block"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "opening_income_tax",
# 			"label": _("Open IT Dep."),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 		{
# 			"fieldname": "it_dep_addition",
# 			"label": _("IT Dep. During the Year"),
# 			"fieldtype": "Currency",
# 			"width": 150
# 		},
# 	]


# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, rounded
from erpnext.accounts.report.financial_statements \
    import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows

def execute(filters=None):
    columns = get_columns()
    data = get_accounts(filters)
    return columns, data

def get_accounts(filters):
    company = filters.get("company")
    data = []
    category_totals = {}  # Dictionary to store summed values by asset category
    company_currency = frappe.db.get_value("Company", company, "default_currency")
    company_symbol = frappe.db.get_value("Currency", company_currency, "symbol")
 
    
    # Get all asset categories and their accounts
    asset_categories = frappe.db.sql("""
        SELECT a.name as category, 
               b.fixed_asset_account as fa, 
                b.accumulated_depreciation_account as acc, 
                b.depreciation_expense_account as dep
        FROM `tabAsset Category` a, 
              `tabAsset Category Account` b
        WHERE a.name = b.parent
        AND a.company = %s
    """, company, as_dict=True)
    for category in asset_categories:
        # Initialize category in totals dictionary if not present
        if category.category not in category_totals:
            category_totals[category.category] = {
                "gross_opening": 0,
                "gross_addition": 0,
                "gross_adjustment": 0,
                "gross_total": 0,
                "dep_opening": 0,
                "dep_addition": 0,
                "dep_adjustment": 0,
                "dep_total": 0,
                "net_block": 0,
                "opening_income_tax": 0,
                "it_dep_addition": 0
            }

        # Get values for this category
        gross_opening = get_values(category.fa, filters.to_date, filters.from_date, filters.cost_center, company, opening=True)[0]
        gross = get_values(category.fa, filters.to_date, filters.from_date, filters.cost_center, company)[0]
        dep_opening = get_values(category.acc, filters.to_date, filters.from_date, filters.cost_center, company, opening=True)[0]
        acc_dep = get_values(category.acc, filters.to_date, filters.from_date, filters.cost_center, company)[0]
        adj = get_values(category.acc, filters.to_date, filters.from_date, filters.cost_center, company, adjustment=True)[0]

        # Calculate values
        g_open = flt(gross_opening.debit) - flt(gross_opening.credit)
        g_addition = flt(gross.debit)
        g_adjustment = flt(gross.credit)
        g_total = g_open + g_addition - g_adjustment
        
        d_open = -1 * (flt(dep_opening.debit) - flt(dep_opening.credit))
        dep_adjust = flt(acc_dep.debit)
        adj_adjust = flt(adj.credit)
        dep_addition = flt(acc_dep.credit) - flt(adj.credit)
        dep_add = flt(acc_dep.credit)
        d_total = d_open + dep_add - flt(dep_adjust)
        
        # Get income tax values
        income_tax = frappe.db.sql("""
            SELECT SUM(b.income_depreciation_amount) as total_income_tax
            FROM `tabAsset` a, `tabDepreciation Schedule` b, `tabAsset Depreciation Schedule` ads
            WHERE ads.name = b.parent
                AND ads.asset = a.name
                AND a.asset_category = %s
                AND a.company = %s
                AND b.schedule_date BETWEEN %s AND CURDATE()
                AND a.docstatus = 1
                AND (
                    a.status NOT IN ('Scrapped', 'Sold')
                    OR
                    (a.status IN ('Scrapped', 'Sold') AND a.disposal_date >= %s)
                )
        """, (category.category, company, filters.from_date, filters.from_date), as_dict=True)

        opening_it_dep = frappe.db.sql("""
            SELECT 
                SUM(b.income_accumulated_depreciation) as acc_income_tax,
                SUM(b.income_depreciation_amount) as depreciation_income_tax
            FROM `tabAsset` a, `tabDepreciation Schedule` b, `tabAsset Depreciation Schedule` ads
            WHERE ads.name = b.parent
                AND ads.asset = a.name
                AND a.asset_category = %s
                AND a.company = %s
                AND (%s BETWEEN b.schedule_start_date AND b.schedule_date
                    OR 
                    (b.schedule_date < %s 
                        AND 
                    b.schedule_date = (SELECT MAX(c.schedule_date) 
                                        FROM `tabDepreciation Schedule` c
                                        WHERE c.parent = ads.name)
                    ))
                AND a.docstatus = 1
                AND (
                    a.status NOT IN ('Scrapped', 'Sold')
                    OR
                    (a.status IN ('Scrapped', 'Sold') AND a.disposal_date >= %s)
                )
        """, (category.category, company, filters.from_date, filters.from_date, filters.from_date), as_dict=True)

        opening_dep = frappe.db.sql("""
            SELECT SUM(a.income_tax_opening_depreciation_amount) as it_opening
            FROM `tabAsset` a
            WHERE a.asset_category = %s
                AND a.company = %s
                AND a.docstatus = 1
                AND (
                    a.status NOT IN ('Scrapped', 'Sold')
                    OR
                    (a.status IN ('Scrapped', 'Sold') AND a.disposal_date >= %s)
                )
                AND NOT EXISTS(
                    SELECT 1
                    FROM `tabDepreciation Schedule` b, `tabAsset Depreciation Schedule` ads
                    WHERE ads.asset = a.name AND b.parent = ads.name
                )    
        """, (category.category, company, filters.from_date), as_dict=True)

        acc_it = opening_it_dep[0].acc_income_tax if opening_it_dep[0].acc_income_tax else 0.00
        depreciation_it = opening_it_dep[0].depreciation_income_tax if opening_it_dep[0].depreciation_income_tax else 0.00
        it_opening = opening_dep[0].it_opening if opening_dep[0].it_opening else 0.00

        # Sum values by category
        category_totals[category.category]["gross_opening"] += g_open
        category_totals[category.category]["gross_addition"] += g_addition
        category_totals[category.category]["gross_adjustment"] += g_adjustment
        category_totals[category.category]["gross_total"] += g_total
        category_totals[category.category]["dep_opening"] += d_open
        category_totals[category.category]["dep_addition"] += dep_addition
        category_totals[category.category]["dep_adjustment"] += dep_adjust
        category_totals[category.category]["dep_total"] += d_total
        category_totals[category.category]["net_block"] += flt(g_total) - flt(d_total)
        category_totals[category.category]["opening_income_tax"] += acc_it - depreciation_it + it_opening
        category_totals[category.category]["it_dep_addition"] += income_tax[0].total_income_tax if income_tax and income_tax[0].total_income_tax else 0.00

    # Convert the summed values to the final data structure
    for category, values in category_totals.items():
        data.append({
            "company": company,
            "asset_category": category,
            "gross_opening": values["gross_opening"],
            "gross_addition": values["gross_addition"],
            "gross_adjustment": values["gross_adjustment"],
            "gross_total": values["gross_total"],
            "dep_opening": values["dep_opening"],
            "dep_addition": values["dep_addition"],
            "dep_adjustment": values["dep_adjustment"],
            "dep_total": values["dep_total"],
            "net_block": values["net_block"],
            "opening_income_tax": values["opening_income_tax"],
            "it_dep_addition": values["it_dep_addition"],
            "currency": company_symbol
        })

    # For CWIP Account
    if flt(filters.include_cwip):
        row = get_cwip(filters)
        data.append(row)
    
    return data

def get_cwip(filters):
    company = filters.get("company")
    cwip_acc = []
    cwip_account = frappe.db.get_value("Company", company, "capital_work_in_progress_account")
    if not cwip_account:
        frappe.throw("Capital Work In Progress Account is missing. Please set CWIP account in Company Setting")
    cwip_accounts_gl = frappe.db.sql("""
        SELECT name FROM tabAccount 
        WHERE parent_account = %s AND company = %s
    """, (cwip_account, company), as_dict=True)
    
    for account in cwip_accounts_gl:
        cwip_acc.append(str(account.name))
    cwip_accounts = tuple(cwip_acc)

    cwip_open = get_values(cwip_accounts, filters.to_date, filters.from_date, filters.cost_center, company, opening=True, cwip=True)
    cwip = get_values(cwip_accounts, filters.to_date, filters.from_date, filters.cost_center, company, cwip=True)

    cwip_open = cwip_open[0] if cwip_open else frappe._dict({"debit": 0.0, "credit": 0.0})
    cwip = cwip[0] if cwip else frappe._dict({"debit": 0.0, "credit": 0.0})

    c_open = flt(cwip_open.debit) - flt(cwip_open.credit)
    c_total = c_open + flt(cwip.debit) - flt(cwip.credit)

    return {
        "company": company,
        "asset_category": "Capital Work in Progress",
        "gross_opening": c_open,
        "gross_addition": cwip.debit,
        "gross_adjustment": cwip.credit,
        "gross_total": c_total,
        "dep_opening": 0,
        "dep_addition": 0,
        "dep_adjustment": 0,
        "dep_total": 0,
        "net_block": 0,
        "opening_income_tax": c_total,
        "it_dep_addition": 0
    }

def get_values(account, to_date, from_date, cost_center=None, company=None, opening=False, cwip=False, adjustment=False):
    if cwip:
        query = """
            SELECT SUM(debit) as debit, SUM(credit) as credit 
            FROM `tabGL Entry` 
            WHERE account IN %s AND docstatus = 1 AND is_cancelled = 0 AND company = %s
        """
        params = [account, company]
    elif adjustment:
        return [frappe._dict({"debit": 0.0, "credit": 0.0})]
    else:
        query = """
            SELECT SUM(debit) as debit, SUM(credit) as credit 
            FROM `tabGL Entry` 
            WHERE account = %s AND docstatus = 1 AND is_cancelled = 0 AND company = %s
        """
        params = [account, company]
        
    if not opening:
        query += " AND posting_date BETWEEN %s AND %s"
        params.extend([from_date, to_date])
    else:
        query += " AND posting_date < %s"
        params.append(from_date)
        
    if cost_center:
        query += " AND cost_center = %s"
        params.append(cost_center)

    query += " AND voucher_type NOT IN ('Period Closing Voucher', 'Asset Movement', 'Bulk Asset Transfer')"
    
    value = frappe.db.sql(query, tuple(params), as_dict=True)
    return value or [frappe._dict({"debit": 0.0, "credit": 0.0})]

def get_columns():  
    return [
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 200
        },
        {
            "fieldname": "asset_category",
            "label": _("Asset Category"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "gross_opening",
            "label": _("Opening Acquisation"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "gross_addition",
            "label": _("Acquisation During the Year"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "gross_adjustment",
            "label": _("Adjustment During the Year"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "gross_total",
            "label": _("Gross Total"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "dep_opening",
            "label": _("Accumulated Dep."),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "dep_addition",
            "label": _("Dep. During the Year"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "dep_adjustment",
            "label": _("Dep. Adjustment During the Year"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "dep_total",
            "label": _("Dep. Total"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "net_block",
            "label": _("Net Block"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "opening_income_tax",
            "label": _("Open IT Dep."),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
        {
            "fieldname": "it_dep_addition",
            "label": _("IT Dep. During the Year"),
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150
        },
    ]