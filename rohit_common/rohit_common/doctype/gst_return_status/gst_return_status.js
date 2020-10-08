// Copyright (c) 2020, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('GST Return Status', {
	refresh: function(frm) {
        frm.disable_save();
	},
	onload: function(frm){
		frm.set_query("address", function(doc) {
			if(!doc.supplier) {
				frappe.throw(__('Please select Supplier'));
			}
			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Supplier',
					link_name: doc.supplier
				}
			};
		});
	},
});
