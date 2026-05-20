frappe.pages['financial-overview-d'].on_page_load = function(wrapper) {

	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Financial Dashboard',
		single_column: true
	});

	let container = $(`
		<div class="p-4">
			<div class="row" id="financial-cards"></div>
		</div>
	`).appendTo(page.main);

	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Dashboard Bank Accounts",
			fields: [
				"name",
				"accounts",
				"account_no"
			],
			limit_page_length: 100
		},
		callback: function(r) {

			if (r.message) {

				r.message.forEach(row => {

					frappe.call({
						method: "erpnext.dk_integration_utils.account_inquiry",
						args: {
							account_no: row.account_no,
						},
						callback: function(res) {

							let balance = 0;
							let account_name = row.accounts;     // TOP NAME
							let payer_name = "-";                // ACCOUNT HOLDER NAME

							if (
								res.message &&
								res.message.response_code == "0000"
							) {
								balance =
									res.message.response_data.balance_info
									.btn_available_balance;

								payer_name =
									res.message.response_data.account_info
									.account_name || "-";
							}

							let card = `
								<div class="col-md-3 mb-4">
									<div class="card shadow-sm border-0">
										<div class="card-body">

											<!-- TOP: ACCOUNT NAME -->
											<h3 class="mb-2 font-weight-bold">
												${account_name}
											</h3>

											<!-- ACCOUNT HOLDER -->
											<p class="text-muted mb-3">
												${payer_name}
											</p>

											<!-- ACCOUNT NUMBER -->
											<p class="text-muted mb-1">
												Account No
											</p>

											<h5 class="mb-3">
												${row.account_no || "-"}
											</h5>

											<!-- BALANCE -->
											<p class="text-muted mb-1">
												Balance
											</p>

											<h2 class="text-primary">
												BTN ${balance}
											</h2>

										</div>
									</div>
								</div>
							`;

							$("#financial-cards").append(card);
						}
					});
				});
			}
		}
	});
};