// Copyright (c) 2017, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('State', {
	refresh: function(frm) {

	},
	onload: function(frm){
	    frm.set_query("country", function(doc){
	        return{
	            "filters":{
	                "known_states": 1
	            }
	        }
	    })
	}
});
