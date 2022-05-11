#  Copyright (c) 2022. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-

import frappe
from frappe.utils import flt
from frappe.utils.background_jobs import enqueue
from ..india_gst_api.einv import einv_needed, generate_irn


def enq_inv_sub():
    """
    Performs Draft Invoice Submission for 14 mins max since it runs every 15 mins
    """
    enqueue(get_docs_to_submit, queue="long", timeout=800)


def enq_einv_create():
    """
    Performs eInvoice jobs for 14 mins max since it runs every 15 mins
    """
    enqueue(make_einvoice_for_docs, queue="long", timeout=800)


def get_unposted_invoices():
    """
    Gets a list of invoices which are not posted in the General Ledger and also the ones
    not posted in Stock Ledger
    """
    gl_not_posted = frappe.db.sql("""SELECT si.name, si.creation FROM `tabSales Invoice` si
        WHERE si.base_grand_total > 0 AND si.docstatus = 1 AND si.name NOT IN (SELECT gle.voucher_no
        FROM `tabGL Entry` gle WHERE gle.voucher_type = 'Sales Invoice'
        AND gle.voucher_no = si.name) ORDER BY si.creation""", as_dict=1)
    for un_si in gl_not_posted:
        sid = frappe.get_doc("Sales Invoice", un_si)
        sid.cancel()
        frappe.db.set_value("Sales Invoice", un_si.name, "docstatus", 0)
        frappe.db.set_value("Sales Invoice", un_si.name, "set_posting_time", 1)
        frappe.db.set_value("Sales Invoice", un_si.name, "marked_to_submit", 1)
        print(f"SI# {un_si.name} not Posted in General Ledger hence Made Draft")


def get_docs_to_submit():
    """
    Submits the Sales Invoices or JV which are marked to Submit
    """
    doc_list = ["Sales Invoice"]
    for doc in doc_list:
        dft_doc = frappe.db.sql(f"""SELECT name FROM `tab{doc}` WHERE docstatus = 0
            AND marked_to_submit = 1""", as_dict=1)
        if dft_doc:
            for dtd in dft_doc:
                try:
                    doc_t = frappe.get_doc(doc, dtd.name)
                    doc_t.submit()
                except Exception as e:
                    print(e)


def make_einvoice_for_docs():
    """
    Makes the einvoice for the Docs based on eInvoice Applicability and its Date
    """
    doc_list = ["Sales Invoice"]
    einv_app = flt(frappe.get_value("Rohit Settings", "Rohit Settings", "enable_einvoice"))
    einv_date = frappe.get_value("Rohit Settings", "Rohit Settings", "einvoice_applicable_date")
    if einv_app == 1:
        for doc in doc_list:
            query = f"""SELECT name, posting_date FROM `tab{doc}` WHERE docstatus = 1 AND
            (irn IS NULL OR ack_no IS NULL OR ack_date IS NULL) AND
            posting_date >= '{einv_date}' ORDER BY posting_date DESC, name DESC"""
            einv_docs = frappe.db.sql(query, as_dict=1)
            if einv_docs:
                for einv in einv_docs:
                    need_einv = einv_needed(doc, einv.name)
                    if need_einv == 1:
                        try:
                            print(f"Trying to Generate eInvoice for {doc}: {einv.name}")
                            generate_irn(dtype=doc, dname=einv.name)
                        except Exception as e:
                            print(e)


def make_eway_bill_for_docs():
    """
    If eway is needed for a doc then eway bill is made based on IRN generated
    """
    pass
