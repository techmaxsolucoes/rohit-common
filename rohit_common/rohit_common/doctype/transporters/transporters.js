// Copyright (c) 2020, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporters', 'self_pickup', function(frm){
    frm.doc.gstin_for_eway = ''
    frm.refresh_fields()
});
