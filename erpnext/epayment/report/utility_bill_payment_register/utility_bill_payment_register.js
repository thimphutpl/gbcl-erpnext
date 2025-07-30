// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Utility Bill Payment Register"] = {
	"filters": [
		
        {
            fieldname: "supplier",
            label: "Supplier",
            fieldtype: "Link",
            options: "Supplier"
        },
        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options:["","Completed", "Pending", "Draft", "Waiting for Verification", "Waiting Approval", "Approved", "Rejected", "Failed", "Partial Payment", "Cancelled", "In progress", "Upload Failed", "Waiting Acknowledgement", "Processing Acknowledgement"]
        },
        {
            fieldname: "party",
            label: "Party",
            fieldtype: "Link",
            options: "Supplier"
        },
        {
            fieldname: "branch",
            label: "Branch",
            fieldtype: "Link",
            options: "Branch"
        }
	]
};
