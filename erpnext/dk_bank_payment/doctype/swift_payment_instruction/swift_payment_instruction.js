// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("SWIFT Payment Instruction", {
	refresh(frm) {

	},
    get_details: function(frm){
		get_entries(frm);
	},
});

function get_entries(frm){
	
	if (frm.doc.transaction_id){
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