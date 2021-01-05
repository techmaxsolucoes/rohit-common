# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from rohit_common.utils.rohit_common_utils import validate_email_addresses


def validate(doc, method):
    if doc.email:
        valid_email = validate_email_addresses(doc.email)
        if valid_email == 1:
            frappe.msgprint(f"Email = {doc.email} has been Validated")
