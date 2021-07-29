# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import time

def execute():
    st_time = time.time()
    records_updated = 0
    sid_wrong_gst_hsn = frappe.db.sql("""SELECT sid.name, sid.item_code ,sid.gst_hsn_code,
        it.customs_tariff_number as correct_gst_hsn
        FROM `tabSales Invoice Item` sid, `tabItem` it
        WHERE sid.gst_hsn_code != it.customs_tariff_number AND it.name = sid.item_code
        ORDER BY sid.creation""", as_dict=1)
    if sid_wrong_gst_hsn:
        for sid in sid_wrong_gst_hsn:
            sid_doc = frappe.get_doc("Sales Invoice Item", sid.name)
            if sid.correct_gst_hsn:
                records_updated += 1
                frappe.db.set_value("Sales Invoice Item", sid.name, "gst_hsn_code", sid.correct_gst_hsn)
                # print("Updated CETSH Number and GST HSN Code in Sales Invoice # "
                #        + sid_doc.parent + " Item No: " + str(sid_doc.idx))
            else:
                print("SI# " + sid_doc.parent + " Item Code: " + sid[1] +
                        " At Row No " + str(sid_doc.idx) +
                        " Does Not Have CETSH Number Linked")
    print(f"Total Time Taken = {int(time.time() - st_time)} seconds for Updating GST HSN Codes in {records_updated} items")
