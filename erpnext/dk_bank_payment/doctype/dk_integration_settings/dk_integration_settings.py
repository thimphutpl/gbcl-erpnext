# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DKIntegrationSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_inquiry: DF.Data | None
		authorization_token: DF.Data | None
		base_url: DF.Data | None
		bearer_token: DF.Password | None
		client_id: DF.Data | None
		client_secret: DF.Password | None
		fetch_key: DF.Data | None
		gl_statement: DF.Data | None
		gl_turnover: DF.Data | None
		grand_type: DF.Data | None
		intrabank_transfer: DF.Data | None
		oro_endpoint: DF.Data | None
		password: DF.Data | None
		product_type: DF.Data | None
		source_app: DF.Data | None
		transaction_status: DF.Data | None
		user_name: DF.Data | None
		x_gravitee_api_key: DF.Data | None
	# end: auto-generated types
	pass
