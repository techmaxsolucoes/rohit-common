// Copyright (c) 2020, Rohit Industries Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('eWay Bill', {
	// refresh: function(frm) {

	// }
	onload: function(frm){
        if (frm.doc.document_type === 'Sales Invoice'){
            frm.set_query('document_number', function(doc){
                return {
                    "filters": [
                        ['base_grand_total', '>=', 50000],
                        ['docstatus', '=', 1]
                    ]
                }
            });
        } else if (frm.doc.document_type === 'Purchase Order'){
            frm.set_query('document_number', function(doc){
                return{
                    query: "rohit_common.rohit_common.doctype.eway_bill.eway_bill.ewb_po_query"
                }
            });
        }
	    frm.set_query('document_type', function(doc){
	        return {
				"filters": [
					['name', 'in', ['Delivery Note', 'Purchase Order', 'Purchase Invoice', 'Sales Invoice']]
				]
	        }
	    });
	},
});

frappe.ui.form.on('eWay Bill', 'document_type', function(frm){
    frm.doc.document_number = '';
    frm.doc.approx_distance = '';
    frm.doc.ewb_doc_no = '';
    frm.doc.items = [];
    frm.doc.vehicles = [];
    frm.refresh_fields();
    if (frm.doc.document_type === 'Sales Invoice'){
        frm.set_query('document_number', function(doc){
            return {
                "filters": [
                    ['base_grand_total', '>=', 50000],
                    ['docstatus', '=', 1]
                ]
            }
        });
    } else if (frm.doc.document_type === 'Purchase Order'){
        frm.set_query('document_number', function(doc){
            return{
                query: "rohit_common.rohit_common.doctype.eway_bill.eway_bill.ewb_po_query"
            }
        });
    }
});

frappe.ui.form.on('eWay Bill', 'document_number', function(frm){
    frm.doc.approx_distance = '';
    frm.doc.ewb_doc_no = '';
    frm.doc.items = [];
    frm.doc.vehicles = [];
    frm.refresh_fields();
});
