// Copyright (c) 2020, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rohit Settings', 'sandbox_mode', function(frm){
    frm.doc.access_token_time = '' ;
    frm.doc.access_token = '' ;
    cur_frm.refresh_fields();
});
