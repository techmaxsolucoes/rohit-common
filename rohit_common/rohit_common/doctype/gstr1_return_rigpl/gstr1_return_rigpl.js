// Copyright (c) 2021, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('GSTR1 Return RIGPL', {
	onload: function(frm) {
	    frm.set_query("address", function(doc){
	        return{
	            filters: {
	                "is_your_company_address": 1
	            }
	        }
	    });

	}
});
