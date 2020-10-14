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

frappe.ui.form.on("Address", {
    onload: function(frm){
        frm.set_query("state_rigpl", function(doc){
            return {
				"filters": {
					"country": frm.doc.country
				}
            };
        });
    },
	onload_post_render(frm) {
		if (frm.doc.latitude && frm.doc.longitude) {
		    frappe.msgprint('Hello')
		    var marker = L.marker([frm.doc.latitude, frm.doc.longitude]).addTo(frm.fields_dict.location.map);
		    marker.bindPopup(frm.doc.address_title).openPopup();
			frm.fields_dict.location.map.setView([frm.doc.latitude, frm.doc.longitude], 20);
		}
		else {
			frm.doc.latitude = frm.fields_dict.location.map.getCenter()['lat'];
			frm.doc.longitude = frm.fields_dict.location.map.getCenter()['lng'];
		}
	},
});