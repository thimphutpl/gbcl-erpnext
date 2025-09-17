// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("GL Account Mapping", {
	refresh(frm) {
        if (frm.doc.company){
            frm.set_query("account", function() {
                return {
                    filters: {
                        company: frm.doc.company,
                        is_group: 0  // for example, only ledger accounts
                    }
                };
            });
        }
        
	},

    company: function(frm){
        frm.set_query("account", function() {
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 0  // for example, only ledger accounts
                }
            };
        });
    }
});
