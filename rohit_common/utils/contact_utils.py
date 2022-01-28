# Copyright (c) 2022, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from rohit_common.utils.email_utils import single_email_validations


def validate_contact_emails(con_doc, backend=True):
    """
    Validates the emails in a Contact document's Email Table
    If row in table has multiple email IDs then it would separate the row in to multiple rows
    Also it would remove the invalid emails and also would populate the email address field
    """
    remove_emails = []
    for row in con_doc.email_ids:
        emails = row.email_id.split(',')
        for email in emails:
            valid_email = single_email_validations(email, backend=backend)
            if valid_email:
                # Valid Email if its 1st Email then replace the email in row else add a new row
                if emails.index(email) == 0:
                    row.email_id = valid_email
                else:
                    #Add row to the table with new email ID
                    con_doc.append("email_ids", {"email_id": valid_email})
            else:
                remove_emails.append(email)
    if remove_emails:
        for rmv_eml in remove_emails:
            [con_doc.email_ids.remove(eml) for eml in con_doc.get('email_ids')
            if eml.email_id == rmv_eml]



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
