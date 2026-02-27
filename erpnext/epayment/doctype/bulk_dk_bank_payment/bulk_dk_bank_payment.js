// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk DK Bank Payment", {
    refresh(frm) {},

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

    get_transactions(frm) {
        frappe.call({
            method: "run_doc_method",
            args: {
                docs: frm.doc,
                method: "get_entries"  // this calls the Python method inside the class
            },
            freeze: true,
            freeze_message: "Fetching Transaction Details.... Please Wait",
            callback: function(r){
                if(r.message) {
                    // Clear existing child table
                    frm.clear_table("transaction");

                    // r.message is an array of salary slips
                    r.message.forEach(function(trx) {
                        let row = frm.add_child("transaction");
                        row.employee = trx.employee;
                        row.gross_pay = trx.gross_pay;
                        row.amount = trx.net_pay;
                        row.beneficiary_account_no = trx.bank_ac_no;
                        row.bank_name = trx.bank_name;
                        row.beneficiary_name = trx.employee_name;
                        // add other fields as needed
                    });

                    frm.refresh_field("transaction");
                }
            }
        });
    }
});