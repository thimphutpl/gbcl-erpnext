# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Date


def execute(filters=None):
    columns, data = [], []

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def validate_filters(filters):
    if not filters:
        frappe.throw(_("Please set filters"))

    for field in ["company", "from_date", "to_date", "location"]:
        if not filters.get(field):
            frappe.throw(_("Please set {0}").format(field))


def get_data(filters):
    vpr = frappe.qb.DocType("Visitor Pass Registry")
    item = frappe.qb.DocType("Visitor Pass Registry Item")
 

    # if filters.get("cashier"):
    #     condition.append
    query = (
        frappe.qb.from_(vpr)
        .inner_join(item)
        .on(vpr.name == item.parent)
        .select(
            vpr.posting_date.as_("date"),
            vpr.location,
            item.amount,
            item.ticket_type,
            item.ticket_price,
        	vpr.cashier,
            item.mode_of_payment
        )
        .where(
            (vpr.company == filters.get("company"))
            & (vpr.location == filters.get("location"))
            & (Date(vpr.posting_date) >= filters.get("from_date"))
            & (Date(vpr.posting_date) <= filters.get("to_date"))
            
        )
    )
    if filters.get("ticket_type"):
        query = query.where(item.ticket_type == filters.get("ticket_type"))
        
    if filters.get("mode_of_payment"):
        query = query.where(item.mode_of_payment == filters.get("mode_of_payment"))
        
    if filters.get("cashier"):
        query = query.where(vpr.cashier == filters.get("cashier"))
    
    
    data = query.run(as_list=True)
    return data



def get_columns():
    columns = [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "location",
            "label": _("Location"),
            "fieldtype": "Link",
            "options": "Location",
            "width": 140,
        },
        {
            "fieldname": "total_amount",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldtype": "Link",
            "label": _("Ticket Type"),
            "fieldname": "ticket_type",
            "options": "Ticket Type",
            "width": 150,
        },
        {
            "fieldtype": "Currency",
            "label": _("Ticket Price"),
            "fieldname": "ticket_price",
            "width": 150,
        },
        {
            "fieldtype": "Link",
            "label": _("Cashier"),
            "fieldname": "cashier",
            "options": "User",
            "width": 150,
        },
        {
            "fieldtype": "Link",
            "label": _("Mode of Payment"),
            "fieldname": "mode_of_payment",
            "options": "Mode of Payment",
            "width": 150,
        },
    ]
    return columns