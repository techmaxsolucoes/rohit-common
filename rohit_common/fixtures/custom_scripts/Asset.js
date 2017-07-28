frappe.ui.form.on('Asset', {
	make_schedules_editable: function(frm) {
		var is_editable = frm.doc.manual_depreciation_schedule===1 ? true : false;
		frm.toggle_enable("schedules", is_editable);
		frm.fields_dict["schedules"].grid.toggle_enable("schedule_date", is_editable);
		frm.fields_dict["schedules"].grid.toggle_enable("depreciation_amount", is_editable);
	}
});