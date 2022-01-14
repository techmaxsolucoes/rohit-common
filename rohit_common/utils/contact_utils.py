# Copyright (c) 2022, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def get_contact_phones(con_name):
    """
    Returns phone numbers as CSV text for a Contact Name
    """
    phones = ""
    if "'" in con_name:
        cond = f'''"{con_name}"'''
    else:
        cond = f"""'{con_name}'"""
    query = f"""SELECT phone FROM `tabContact Phone`
        WHERE parenttype = 'Contact' AND parent = {cond}"""
    ph_nos = frappe.db.sql(query, as_dict=1)
    if ph_nos:
        for phone_nos in ph_nos:
            if phones == "":
                phones += phone_nos.phone
            else:
                phones += ", " + phone_nos.phone
    return phones


def get_contact_emails(con_name):
    """
    Returns emails for a Contact Name
    """
    emails = ""
    if "'" in con_name:
        cond = f'''"{con_name}"'''
    else:
        cond = f"""'{con_name}'"""
    em_dict = frappe.db.sql(f"""SELECT email_id FROM `tabContact Email`
        WHERE parenttype = 'Contact' AND parent = {cond}""", as_dict=1)
    if em_dict:
        for email in em_dict:
            if emails == "":
                emails += email.email_id
            else:
                emails += ", " + email.email_id
    return emails
