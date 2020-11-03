# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import frappe
from erpnext.controllers.selling_controller import SellingController

def execute():
    start_time = time.time()
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
        if total % 10 == 0:
            bat_st_time = time.time()
        total += 1
        inv_st_time = time.time()
        si_doc = frappe.get_doc("Sales Invoice", si)
        SellingController.update_stock_ledger(si_doc)
        frappe.db.set_value("Sales Invoice", si, "update_stock", 1, update_modified=False)
        inv_end_time = time.time()
        inv_time = int(inv_end_time - inv_st_time)
        print(f"#{total}. Updated {si} and Posted Stock Ledger Entries Time for Invoice: {inv_time} "
              f"seconds")
        if total % 10 == 0 and total != 0:
            frappe.db.commit()
            bat_end_time = time.time()
            batch_time = int(bat_end_time - bat_st_time)
            print(f"Updating the Databases After {total} Entries Total Time for this Batch {batch_time} seconds")
    end_time = time.time()
    total_time = int(end_time - start_time)
    print("Total Invoices Updated = {}".format(len(unique_si_list)))
    print(f"Total Execution Time: {total_time} seconds")