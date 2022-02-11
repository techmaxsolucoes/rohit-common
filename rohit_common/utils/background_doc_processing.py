# -*- coding: utf-8 -*-
# Copyright (c) 2022, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from frappe.utils.background_jobs import enqueue


def enqueue_bg():
    enqueue(process_bg_docs, queue="long", timeout=2700)


def get_bg_docs():
    """
    Returns a list of document types which are enabled for Background processing
    The document type should also have a checkbox with name background_processing
    """
    doc_lst = []
    rset = frappe.get_doc("Rohit Settings", "Rohit Settings")
    for dtd in rset.bg_submit_cancel_docs:
        doc_lst.append(dtd.document_type)
    return doc_lst


def process_bg_docs():
    """
    Processes the background jobs for Document Types
    """
    st_time = time.time()
    dt_lst = get_bg_docs()
    tot_docs = 0
    if dt_lst:
        for dtd in dt_lst:
            print(f"Processing Background Submit or Cancel for {dtd}")
            docs_marked = frappe.db.sql(f"""SELECT name, background_processing, docstatus
            FROM `tab{dtd}` WHERE background_processing = 1 AND (docstatus = 0
            OR docstatus = 1)""", as_dict=1)
            if docs_marked:
                for mkd_dt in docs_marked:
                    mkd_doc = frappe.get_doc(dtd, mkd_dt.name)
                    if mkd_dt.docstatus == 0:
                        tot_docs += 1
                        print(f"Submitting {mkd_doc.name}")
                        mkd_doc.background_processing = 0
                        mkd_doc.save()
                        mkd_doc.submit()
                        frappe.db.commit()
                    elif mkd_dt.docstatus == 1:
                        tot_docs += 1
                        print(f"Cancelling {mkd_doc.name}")
                        mkd_doc.background_processing = 0
                        mkd_doc.save()
                        mkd_doc.cancel()
                        frappe.db.commit()
            else:
                print(f"No Docs in {dtd}")
    print(f"Total Time Taken = {int(time.time() - st_time)} seconds Docs Processed = {tot_docs}")
