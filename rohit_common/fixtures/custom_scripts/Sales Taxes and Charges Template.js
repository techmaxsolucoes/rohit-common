frappe.ui.form.on("Sales Taxes and Charges Template", {
    onload: function(frm){
        frm.set_query("default_bank_account", function(doc){
            return {
				"filters": {
					"is_company_account": 1,
					"verified": 1
				}
            };
        });
    },
});