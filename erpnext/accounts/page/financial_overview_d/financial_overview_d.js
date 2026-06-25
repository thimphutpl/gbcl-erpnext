// frappe.pages['financial-overview-d'].on_page_load = function(wrapper) {

// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Financial Dashboard',
// 		single_column: true
// 	});

// 	let container = $(`
// 		<div class="p-4">
// 			<div class="row" id="financial-cards"></div>
// 		</div>
// 	`).appendTo(page.main);

// 	frappe.call({
// 		method: "frappe.client.get_list",
// 		args: {
// 			doctype: "Dashboard Bank Accounts",
// 			fields: [
// 				"accounts_name",
// 				"name",
// 				"accounts",
// 				"account_no"
// 			],
// 			limit_page_length: 100
// 		},

// 		callback: function(r) {

// 			if (r.message) {

// 				r.message.forEach(row => {

// 					frappe.call({
// 						method: "erpnext.dk_integration_utils.account_inquiry",
// 						args: {
// 							account_no: row.account_no,
// 							accounts_name: row.accounts_name
// 						},
// 						callback: function(res) {

// 							let balance = 0;
// 							let account_name = row.accounts_name;     // TOP NAME
// 							let payer_name = "-";                // ACCOUNT HOLDER NAME

// 							if (
// 								res.message &&
// 								res.message.response_code == "0000"
// 							) {
// 								balance =
// 									res.message.response_data.balance_info
// 									.btn_available_balance;

// 								payer_name =
// 									res.message.response_data.account_info
// 									.account_name || "-";
// 							}

// 							let card = `
// 								<div class="col-md-3 mb-4">
// 									<div class="card shadow-sm border-0">
// 										<div class="card-body">

// 											<!-- TOP: ACCOUNT NAME -->
// 											<h3 class="mb-2 font-weight-bold">
// 											    ${account_name}
												
// 											</h3>

// 											<!-- ACCOUNT HOLDER -->
// 											<p class="text-muted mb-3">
// 												${payer_name}
// 											</p>

// 											<!-- ACCOUNT NUMBER -->
// 											<p class="text-muted mb-1">
// 												Account No
// 											</p>

// 											<h5 class="mb-3">
// 												${row.account_no || "-"}
// 											</h5>

// 											<!-- BALANCE -->
// 											<p class="text-muted mb-1">
// 												Balance
// 											</p>

// 											<h2 class="text-primary">
// 												BTN ${balance}
// 											</h2>

// 										</div>
// 									</div>
// 								</div>
// 							`;

// 							$("#financial-cards").append(card);
// 						}
// 					});
// 				});
// 			}
// 		}
// 	});
// };

frappe.pages['financial-overview-d'].on_page_load = function(wrapper) {

	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Financial Dashboard',
		single_column: true
	});

	// container
	$(`
		<div class="p-3">
			<div class="row" id="financial-cards"></div>
		</div>
	`).appendTo(page.main);

	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Dashboard Bank Accounts",
			fields: [ "accounts_name","name", "accounts", "account_no","sequence"],
			limit_page_length: 100,
			order_by: "sequence asc"
		},
		callback: function(r) {

			if (!r.message) return;

			r.message.forEach(row => {

				frappe.call({
					method: "erpnext.dk_integration_utils.account_inquiry",
					args: {
						account_no: row.account_no,
						accounts_name: row.accounts_name
					},
					callback: function(res) {

						// let account_name = row.accounts || "-";
						let account_name = row.accounts_name || "-";
						let payer_name = "-";

						let btn_balance = "0.00";
						let usd_balance = "0.00";

						if (res.message?.response_code === "0000") {

							let data = res.message.response_data || {};
							let balance = data.balance_info || {};
							let info = data.account_info || {};

							payer_name = info.account_name || "-";

							btn_balance = balance.btn_available_balance || "0.00";
							usd_balance = balance.usd_available_balance || "0.00";
						}

						// =========================
						// ERPNext STYLE CARD
						// =========================
						let card = `
							<div class="col-md-4 mb-4">

								<div class="frappe-card p-3 shadow-sm border rounded">

									<!-- HEADER -->
									<div class="d-flex justify-content-between align-items-start mb-2">

										<div>
											<div class="text-primary font-weight-bold" style="font-size: 16px;">
												${account_name}
											</div>
											<div class="text-muted" style="font-size: 12px;">
												${payer_name}
											</div>
										</div>

										<span class="badge badge-light">
											Bank Account
										</span>

									</div>

									<hr class="my-2">

									<!-- ACCOUNT NO -->
									<div class="mb-2">
										<div class="text-muted" style="font-size: 12px;">
											Account No
										</div>
										<div style="font-weight: 500;">
											${row.account_no}
										</div>
									</div>

									<!-- BALANCES GRID -->
									<div class="row mt-3">

										<div class="col-6">
											<div class="text-muted" style="font-size: 11px;">
												BTN Balance
											</div>
											<div style="font-size: 15px; font-weight: 600; color: #1f7aec;">
												BTN ${btn_balance}
											</div>
										</div>

										<div class="col-6 text-right">
											<div class="text-muted" style="font-size: 11px;">
												USD Balance
											</div>
											<div style="font-size: 15px; font-weight: 600; color: #28a745;">
												USD ${usd_balance}
											</div>
										</div>

									</div>

								</div>
							</div>
						`;

						$("#financial-cards").append(card);
					}
				});
			});
		}
	});
};