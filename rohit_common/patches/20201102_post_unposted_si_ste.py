# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import frappe
from erpnext.controllers.selling_controller import SellingController

def execute():
    si_list = frappe.db.sql("""SELECT si.name, si.docstatus, si.update_stock FROM `tabSales Invoice` si, 
    `tabSales Invoice Item` sid WHERE sid.parent = si.name AND si.docstatus = 1 
    AND sid.delivery_note IS NULL AND si.update_stock = 0 ORDER BY si.posting_date""", as_dict=1)
    unique_si_list = []
    for si in si_list:
        if si.name not in unique_si_list:
            unique_si_list.append(si.name)
    print("Total Invoices to be Updated = {}".format(len(unique_si_list)))
    total = 0
    for si in unique_si_list:
        total += 1
        si_doc = frappe.get_doc("Sales Invoice", si)
        SellingController.update_stock_ledger(si_doc)
        frappe.db.set_value("Sales Invoice", si, "update_stock", 1)
        print("Updated {} and Posted Stock Ledger Entries".format(si))
        if total % 100 == 0 and total != 0:
            frappe.db.commit()
            print("Updating the Databases After {} Entries".format(total))
            time.sleep(5)
    print("Total Invoices Updated = {}".format(len(unique_si_list)))