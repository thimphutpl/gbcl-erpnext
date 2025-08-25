// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("GL Turnover Entry", {
	refresh(frm) {

	},
	
	fetch: function(frm){
		if (frm.doc.date){
			if (frm.doc.company=='Digital Kidu'){
				frappe.call({
					method: "erpnext.cbs_gl_import.doctype.gl_turnover_entry.gl_turnover_entry.handle_glturnover",
					args: {
						date: frm.doc.date,
						doc_name:frm.doc.name,
					},
					freeze: true,
					freeze_message: __("Checking transaction status..."),
					callback: function(r) {
						frappe.dom.unfreeze();
						
						if (r.message) {
							
				
							// Refresh the child table UI
							
							frappe.msgprint(__("Transaction status fetched successfully."));
							frm.refresh_field("items");
	
						   
						} else {
							frappe.throw(__("Unable to fetch Data"));
						}
					}


				});
			}


			if (frm.doc.company=='Oro Bank'){
				frappe.call({
					method: "erpnext.cbs_gl_import.doctype.gl_turnover_entry.gl_turnover_entry.handle_glturnover_oro",
					args: {
						date: frm.doc.date,
						currency:frm.doc.currency,
						doc_name:frm.doc.name,
					},
					freeze: true,
					freeze_message: __("Checking transaction status..."),
					callback: function(r) {
						frappe.dom.unfreeze();
						
						if (r.message) {
							
				
							// Refresh the child table UI
							
							frappe.msgprint(__("Transaction status fetched successfully."));
							frm.refresh_field("items");
	
						   
						} else {
							frappe.throw(__("Unable to fetch Data"));
						}
					}


				});
			}
			
		}
	}
});
