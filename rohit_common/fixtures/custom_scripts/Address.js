cur_frm.add_fetch('state_rigpl','state_code_numeric','gst_state_number');
frappe.ui.form.on('Address', "state_rigpl", function(frm, cdt, cdn){
	var d = locals[cdt][cdn]
	if (d.country === 'India'){
		frappe.model.set_value(cdt, cdn, "gst_state", d.state_rigpl);
		frappe.model.set_value(cdt, cdn, "gst_state_number", d.gstin.substring(0,2));
		cur_frm.refresh_fields();
	}
});
frappe.ui.form.on('Address', "gstin", function(frm, cdt, cdn){
	var d = locals[cdt][cdn]
	frappe.model.set_value(cdt, cdn, "gst_state", d.state_rigpl);
	frappe.model.set_value(cdt, cdn, "gst_state_number", d.gstin.substring(0,2));	
	cur_frm.refresh_fields();
});