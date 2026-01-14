# # Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt


# from frappe.model.document import Document


# class EmployeeGroup(Document):
# 	# begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.setup.doctype.employee_group_table.employee_group_table import EmployeeGroupTable
# 		from frappe.types import DF

# 		employee_group_name: DF.Data
# 		employee_list: DF.Table[EmployeeGroupTable]
# 		employee_pf: DF.Percent
# 		employer_pf: DF.Percent
# 		health_contribution: DF.Currency
# 		minimum_months: DF.Float
# 	# end: auto-generated types

# 	pass


# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class EmployeeGroup(Document):
	def validate(self):
		self.validate_group_items()

	def validate_group_items(self):
		dup = {}
		for i in self.items:
			if i.leave_type in dup:
				frappe.throw(_("Row#{0} : Duplicate Record found for leave type `<b>{1}</b>`").format(i.idx, i.leave_type), title="Duplicate Data")
			else:
				dup.setdefault(i.leave_type, 1)
