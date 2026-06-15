// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// cur_frm.add_fetch("paid_from", "bank_ac_no", "bank_account_no");
frappe.ui.form.on("DK Bank Payment", {

	
	refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.workflow_state!='Completed') { // 1 = Submitted
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
	paid_from: function(frm) {

		if (frm.doc.paid_from) {
			frappe.db.get_value("Account", frm.doc.paid_from, "bank_ac_no", (r) => {
				frm.set_value("bank_account_no", r.bank_ac_no);
			});

		} else {

			// clear everything when removed
			frm.set_value({
				bank_account_no: "",
				bank_balance: "",
				bank_balance_usd: "",
				inquiry_id: "",
				payer_name: "",
				acc_status_details: ""
			});
		}
	},
	
    transaction_code:function(frm){
		if (frm.doc.transaction_code == 'Intrabank transfer'){
			frm.set_query("pay_to_bank", function() {
				return {
					filters: {
						intra_bank: 1
					}
				};
			});
		}
		else{frm.set_query("pay_to_bank", function() {
			return {
				filters: {
					intra_bank: 0
				}
			};
		});}
	},

    bank_account_no: function(frm){
		  if (!frm.doc.bank_account_no || !frm.doc.paid_from) {
        return;
    }
		frappe.dom.freeze('Fetching bank details...');
        frappe.call({
			method: "erpnext.dk_integration_utils.account_inquiry",
			args: {
				account_no: frm.doc.bank_account_no,
			},
			callback: function(r) {
				// console.log('hihi')
				// console.log(frm.doc.transaction_code);
				frappe.dom.unfreeze();
				if(r.message) {
					console.log(r.message);

					if(r.message.response_code == "0000"){
						
				    

						frm.set_value("bank_balance", r.message.response_data.balance_info.btn_available_balance);
                        frm.set_value("bank_balance_usd", r.message.response_data.balance_info.usd_available_balance);
						
						
						 frm.set_value("inquiry_id",r.message.response_data.meta_info.inquiry_id);
                         frm.set_value("payer_name",r.message.response_data.account_info.account_name);
						//  frm.set_value("bank_balance_usd",r.message.response_data.balance_info.usd_available_balance);
						 frm.set_value("acc_status_details",r.message.response_data.account_status.acc_status_details);
					}
					else{
						frappe.throw("Unable to fetch Bank Balance");
					}
						
				}
			}
		});
    },

	


	get_transactions: function(frm){
		get_entries(frm);
	},
});




function get_entries(frm){
	
	cur_frm.clear_table("transaction");
	
	if (frm.doc.transaction_type){
		frappe.call({
			method: "get_entries",
			doc: cur_frm.doc,
			callback: function(r){
				if(r.message){
					// cur_frm.set_value('total_amount', r.message);
				}
				cur_frm.refresh_fields();
			},
			freeze: true,
            freeze_message: "Fetching Transaction Details.... Please Wait",
		});
	}
	cur_frm.refresh_fields();
}