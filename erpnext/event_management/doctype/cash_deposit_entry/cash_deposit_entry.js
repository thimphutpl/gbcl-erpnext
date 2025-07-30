// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cash Deposit Entry", {
    setup(frm) {
        frm.set_query("location", function(){
			return {
				filters: {
					'disabled': 0,
					'is_recreational_park': 1,
				}
			}
		});
    },

	refresh(frm) {
		refresh_html(frm);
	},

	location: (frm) => {
		frm.trigger("get_reference_document");
    },

	from_date: (frm) => {
		frm.trigger("get_reference_document");
    },

    to_date: (frm) => {
		frm.trigger("get_reference_document");
    },

	get_reference_document: function(frm) {
		reset_values(frm);
		if (frm.doc.location) {
			frappe.call({
				method: "get_transaction_detail",
				doc: frm.doc,
				callback: function(r) {
					if(r.message) {
						let docs = r.message;
						set_form_data(docs, frm);
						refresh_fields(frm);
					}
				}
			});
		}
	}
});

function reset_values(frm) {
	frm.set_value("items", []);
	frm.set_value("total_amount", 0);
}

function set_form_data(data, frm) {
	data.forEach((d) => {
		add_reference_docs(d, frm);
		frm.doc.total_amount += flt(d.cash_amount);
	});
}

function add_reference_docs(d, frm) {
	frm.add_child("items", {
		reference_name: d.reference_name,
		posting_date: d.posting_date,
		cash_amount: d.cash_amount,
		cashier: d.cashier,
	});
}

function refresh_fields(frm) {
	frm.refresh_field("items");
	frm.refresh_field("total_amount");
}

var refresh_html = function(frm){
	var journal_entry_status = "";
	if(frm.doc.journal_entry_status){
		journal_entry_status = '<div style="font-style: italic; font-size: 0.8em; ">* '+frm.doc.journal_entry_status+'</div>';
	}
	
	if(frm.doc.journal_entry){
		$(cur_frm.fields_dict.journal_entry_html.wrapper).html('<label class="control-label" style="padding-right: 0px;">Journal Entry</label><br><b>'+'<a href="/desk/Form/Journal Entry/'+frm.doc.journal_entry+'">'+frm.doc.journal_entry+"</a> "+"</b>"+journal_entry_status);
	}	
}
