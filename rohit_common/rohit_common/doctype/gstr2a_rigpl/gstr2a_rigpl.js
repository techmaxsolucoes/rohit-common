// Copyright (c) 2021, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('GSTR2A RIGPL', {
	refresh: function(frm) {
	},
	onload: function(frm){
		frm.set_query("company_address", function(doc) {
			return {
				"filters": {
					"is_your_company_address": 1
				}
			};
		});
		frm.set_query("party_type", "invoices", function(doc, cdt, cdn) {
			return {
				"filters": [
					['name', 'in', ['Customer', 'Supplier']]
				]
			};
		});
		frm.set_query("linked_document_type", "invoices", function(doc, cdt, cdn) {
			return {
				"filters": [
					['name', 'in', ['Purchase Invoice', 'Journal Entry']]
				]
			};
		});
	},
});
