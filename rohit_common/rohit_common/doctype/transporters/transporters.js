// Copyright (c) 2020, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporters', 'self_pickup', function(frm){
    frm.doc.gstin_for_eway = ''
    frm.doc.track_on_shipway = 0
    frm.doc.fedex_credentials = 0
    frm.doc.fedex_tracking_only = 0
    frm.doc.dtdc_credentials = 0
    frm.refresh_fields()
});

frappe.ui.form.on('Transporters', 'track_on_shipway', function(frm){
    frm.doc.gstin_for_eway = ''
    frm.doc.self_pickup = 0
    frm.doc.fedex_credentials = 0
    frm.doc.fedex_tracking_only = 0
    frm.doc.dtdc_credentials = 0
    frm.refresh_fields()
});

frappe.ui.form.on('Transporters', 'fedex_credentials', function(frm){
    frm.doc.gstin_for_eway = ''
    frm.doc.self_pickup = 0
    frm.doc.track_on_shipway = 0
    frm.doc.fedex_tracking_only = 0
    frm.doc.dtdc_credentials = 0
    frm.refresh_fields()
});

frappe.ui.form.on('Transporters', 'fedex_tracking_only', function(frm){
    frm.doc.gstin_for_eway = ''
    frm.doc.self_pickup = 0
    frm.doc.track_on_shipway = 0
    frm.doc.fedex_credentials = 0
    frm.doc.dtdc_credentials = 0
    frm.refresh_fields()
});

frappe.ui.form.on('Transporters', 'dtdc_credentials', function(frm){
    frm.doc.gstin_for_eway = ''
    frm.doc.self_pickup = 0
    frm.doc.track_on_shipway = 0
    frm.doc.fedex_credentials = 0
    frm.doc.fedex_tracking_only = 0
    frm.refresh_fields()
});
