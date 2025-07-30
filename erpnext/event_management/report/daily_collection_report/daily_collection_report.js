frappe.query_reports["Daily Collection Report"] = {
    "filters": [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,  // Required
        },
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
            fieldname: "ticket_type",
            label: __("Ticket Type"),
            fieldtype: "Link",
            options: "Ticket Type",
        },
		{
            fieldname: "mode_of_payment",
            label: __("Mode of Payment"),
            fieldtype: "Link",
            options: "Mode of Payment",
        },
		{
            fieldname: "cashier",
            label: __("Cashier"),
            fieldtype: "Link",
            options: "User",
        },
    ]
};