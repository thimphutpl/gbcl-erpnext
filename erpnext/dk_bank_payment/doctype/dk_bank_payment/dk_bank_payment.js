// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("DK Bank Payment", {
	
	refresh: function(frm) {
        if (frm.doc.docstatus === 1) { // 1 = Submitted
            frm.add_custom_button(__('Check Transaction Status'), function () {

                frappe.call({
                    method: "erpnext.dk_bank_payment.doctype.dk_bank_payment.dk_bank_payment.check_transaction_status",
                    args: {
                        doc: frm.doc
                    },
                    freeze: true,
                    freeze_message: __("Checking transaction status..."),
                    callback: function(r) {
                        frappe.dom.unfreeze();
                        
                        if (r.message) {
                            console.log("hi");
                            frappe.msgprint(__("Transaction status fetched successfully."));
                        } else {
                            frappe.throw(__("Unable to fetch Bank Balance"));
                        }
                    }
                });

            });
        }
    },

    bank_account_no: function(frm){
		frappe.dom.freeze('Fetching bank details...');
        frappe.call({
			method: "erpnext.dk_integration_utils.account_inquiry",
			args: {
				account_no: frm.doc.bank_account_no,
			},
			callback: function(r) {
				frappe.dom.unfreeze();
				if(r.message) {
					console.log(r.message);
					if(r.message.response_code == "0000"){
						 frm.set_value("bank_balance", r.message.response_data.balance_info.btn_available_balance);
						 frm.set_value("inquiry_id",r.message.response_data.meta_info.inquiry_id);
						 frm.set_value("bank_balance_usd",r.message.response_data.balance_info.usd_available_balance);
						 frm.set_value("acc_status_details",r.message.response_data.account_status.acc_status_details);
					}
					else{
						frappe.throw("Unable to fetch Bank Balance");
					}
						
				}
			}
		});
    }
});
