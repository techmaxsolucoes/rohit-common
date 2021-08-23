#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def validate(doc, method):
    avg_days = get_average_credit_days(doc)
    doc.average_credit_days = avg_days
    if doc.average_credit_days > 0:
        doc.credit_given = 1
        doc.check_clearance_of_payment = 0
    else:
        doc.credit_given = 0


def get_average_credit_days(doc):
    avg_days = 0
    invoice_portion = 0
    if doc.terms:
        for d in doc.terms:
            invoice_portion += d.invoice_portion / 100
            ptd = frappe.get_doc("Payment Term", d.payment_term)
            d.credit_days = ptd.credit_days
            avg_days += int(d.invoice_portion * d.credit_days / 100)
        if invoice_portion > 1:
            frappe.throw(f"Total Invoice Portion cannot be More than 100% {invoice_portion}")
    else:
        frappe.throw(f"Terms Table is Needed in Payment Terms Template")
    return avg_days
