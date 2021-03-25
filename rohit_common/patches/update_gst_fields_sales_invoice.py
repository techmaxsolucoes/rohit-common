#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# Updates the GST Fields for Enabled Sales Taxes and Charges only
import frappe
import time


def execute():
    st_time = time.time()
    enabled_st = frappe.db.sql("""SELECT st.name, st.from_address, adr.gstin, st.export_type, st.is_export
    FROM `tabSales Taxes and Charges Template` st, `tabAddress` adr 
    WHERE st.disabled = 0 AND st.from_address = adr.name""", as_dict=1)
    wrong_invoices = 0
    for st in enabled_st:
        print(f"Processing Invoices with ST Template = {st.name}")
        query = """SELECT si.name, si.company_address, si.company_gstin, si.place_of_supply, si.posting_date, 
        si.taxes_and_charges, si.customer_address, si.gst_category, si.export_type, si.port_code, si.transporters 
        FROM `tabSales Invoice` si, `tabSales Taxes and Charges Template` st 
        WHERE st.name = si.taxes_and_charges AND si.taxes_and_charges = '%s' AND si.base_net_total > 0 
        AND st.is_sample = 0 ORDER BY si.name""" % st.name
        inv_list = frappe.db.sql(query, as_dict=1)
        for inv in inv_list:
            print(f"Processing {inv.name}")
            changes_made = 0
            cust_state = frappe.db.get_value("Address", inv.customer_address, "state")
            if inv.place_of_supply != cust_state:
                frappe.db.set_value("Sales Invoice", inv.name, "place_of_supply", cust_state)
                changes_made += 1
            if inv.company_address != st.from_address:
                if changes_made == 0:
                    changes_made += 1
                addr_doc = frappe.get_doc("Address", st.from_address)
                frappe.db.set_value("Sales Invoice", inv.name, "company_address", addr_doc.name)
                frappe.db.set_value("Sales Invoice", inv.name, "company_gstin", addr_doc.gstin)

            if st.is_export == 1:
                tpt_doc = frappe.get_doc("Transporters", inv.transporters)
                frappe.db.set_value("Sales Invoice", inv.name, "gst_category", "Overseas")
                frappe.db.set_value("Sales Invoice", inv.name, "export_type", st.export_type)
                frappe.db.set_value("Sales Invoice", inv.name, "port_code", tpt_doc.port_code[:6])
                try:
                    brc = frappe.db.sql("""SELECT name FROM `tabBRC MEIS Tracking` WHERE reference_name='%s' 
                    AND reference_doctype='%s' AND docstatus != 2""" % (inv.name, "Sales Invoice"), as_list=1)
                    if brc:
                        brc_doc = frappe.get_doc("BRC MEIS Tracking", brc[0][0])
                        if inv.shipping_bill_number != brc_doc.shipping_bill_number:
                            frappe.db.set_value("Sales Invoice", inv.name, "shipping_bill_number",
                                                brc_doc.shipping_bill_number)
                            frappe.db.set_value("Sales Invoice", inv.name, "shipping_bill_date",
                                    brc_doc.shipping_bill_date)
                except Exception as e:
                    print(f"Some Error for {inv.name} and Error = {e}")

            wrong_invoices += changes_made
        print(f"Completed SI for {st.name} and Total Time Taken = {int(time.time() - st_time)} seconds")
    print(f"Total Wrong Invoices = {wrong_invoices} and Total Time Taken = {int(time.time() - st_time)} seconds")
