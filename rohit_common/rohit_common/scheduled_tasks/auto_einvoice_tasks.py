#  Copyright (c) 2022. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-

import frappe
from frappe.utils import flt
from frappe.utils.background_jobs import enqueue
from ..india_gst_api.einv import generate_irn


def enqueue_einvoice_jobs():
    """
    Performs eInvoice jobs for 14 mins max since it runs every 15 mins
    """
    enqueue(perform_einvoice_auto_tasks, queue="long", timeout=800)


def perform_einvoice_auto_tasks():
    """
    Does the following tasks
    1. Gets SI or JV marked to submit and submits them.
    2. If einvoice is activated then checks if einvoice is needed to be raised and raises the same.
    3. If eWay is needed then would generate the eway Bill as well after raising the einvoice
    """
    get_docs_to_submit()
    make_einvoice_for_docs()
    # make_eway_bill_for_docs()


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
                    frappe.db.commit()
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
