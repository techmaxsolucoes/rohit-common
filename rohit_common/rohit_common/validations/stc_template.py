# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def validate(doc, method):
    if doc.is_export == 1 and doc.is_sample != 1:
        if not doc.iec_code:
            frappe.throw('For Export Related Taxes IEC Code is Mandatory')
        if not doc.bank_ad_code:
            frappe.throw('For Export Related Taxes Bank AD Code is Mandatory')
        if not doc.bank_ifsc_code:
            frappe.throw('For Export Related Taxes Bank IFSC Code is Mandatory')
        if not doc.export_type:
            frappe.throw('For Export Related Taxes Export Type is Mandatory')
    if doc.is_export != 1:
        if not doc.state:
            frappe.throw('For Local or Central Sales State is Mandatory')