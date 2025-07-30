// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Fee Summary Report"] = {
	"filters": [
		{
            fieldname: "location",
            label: __("Location"),
            fieldtype: "Link",
            options: "Location",
            reqd: 1,  // Required
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,  // Required
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,  // Required
        },
		{
            fieldname: "mode_of_payment",
            label: __("Mode of Payment"),
            fieldtype: "Link",
            options: "Mode of Payment",
        },
	]
};
