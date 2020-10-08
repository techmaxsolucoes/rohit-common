# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import time


def execute():
    doc_list = ['Purchase Order', 'Purchase Invoice', 'Sales Invoice']
    for d in doc_list:
        if d == 'Sales Invoice':
            field_name = 'company_address'
            tax_dt = 'Sales Taxes and Charges Template'
        else:
            field_name = 'billing_address'
            tax_dt = 'Purchase Taxes and Charges Template'
        all_docs = frappe.db.sql("""SELECT name FROM `tab%s` ORDER BY creation"""%(d), as_list=1)
        for doc in all_docs:
            print("Checking {} # {}".format(d, doc[0]))
            doc_doc = frappe.get_doc(d, doc[0])
            for item in doc_doc.items:
                hsn_code = frappe.get_value('Item', item.item_code, 'customs_tariff_number')
                if item.gst_hsn_code != hsn_code:
                    print('Updated HSN Code for Row# {}'.format(item.idx))
                    frappe.db.set_value('%s Item'%(d), item.name, "gst_hsn_code", hsn_code)
            if doc_doc.taxes_and_charges:
                txt_tmp_doc = frappe.get_doc(tax_dt, doc_doc.taxes_and_charges)
                if txt_tmp_doc.disabled != 1:
                    from_gstin = frappe.db.get_value('Address', txt_tmp_doc.from_address, "gstin")
                    if txt_tmp_doc.from_address != doc_doc.get(field_name):
                        frappe.db.set_value(d, doc_doc.name, field_name, txt_tmp_doc.from_address)
                        print ('Updated {}# {} for {}'.format(d, doc[0], field_name))
                    if from_gstin != doc_doc.company_gstin:
                        frappe.db.set_value(d, doc_doc.name, "company_gstin", from_gstin)
                        print ('Updated {}# {} for Company GSTIN'.format(d, doc_doc.name))
                else:
                    print("{} Disabled for {} # {}".format(doc_doc.taxes_and_charges, d, doc_doc.name))
            else:
                print("Skipping {} # {}".format(d, doc[0]))
        print('Saving Changes to {}'.format(d))
        time.sleep(2)
        frappe.db.commit()
