# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import frappe
from frappe.core.doctype.file.file import File


def validate(doc, method):
    check_file_availability(doc)
    # If File being created is Public then check if the Doctype its attached to is allowed or not.
    # If Doctype is not allowed then check if the role is allowed to create Public Files or not.
    if doc.is_private != 1:
        rset = frappe.get_doc("Rohit Settings")
        user = frappe.get_user()
        # Check if doctype is allowed in Settings if No then check if the User Role is allowed in Settings
        doc_allowed = 0
        role_allowed = 0
        for role in rset.roles_allow_pub_att:
            if role.role in user.roles:
                role_allowed = 1
        if doc.attached_to_doctype:
            for dt in rset.docs_with_pub_att:
                if doc.attached_to_doctype == dt.document_type:
                    doc_allowed = 1
                    break
            if doc_allowed != 1:
                if role_allowed == 1:
                    frappe.throw(f"{doc.file_name} that you are trying to Attached to "
                                 f"{frappe.get_desk_link(doc.attached_to_doctype, doc.attached_to_name)} is Public "
                                 f"File.\n You are allowed to create Public Files but {doc.attached_to_doctype} is Not "
                                 f"Mentioned in Rohit Settings.\nKindly Mention {doc.attached_to_doctype} to "
                                 f"Create a Public File with this Doctype or Make this File Private")
                else:
                    frappe.throw(f"{user.name} is Not Allowed to Create Public Files.\nKindly make this Attachment "
                                 f"Private to Proceed.")
        else:
            if role_allowed != 1:
                frappe.throw(f"{doc.file_name} is Not Attached to Any Doctype and {user.name} is Not Allowed to Create "
                             f"Public Attachments.\nKindly make this Attachment Private to Proceed.")
        if role_allowed == 1:
            if doc_allowed == 1:
                pass
            else:
                if doc.attached_to_doctype:
                    frappe.throw(f"{doc.file_name} that you are trying to Attached to "
                                 f"{frappe.get_desk_link(doc.attached_to_doctype, doc.attached_to_name)} is Public File."
                                 f"\n You are allowed to create Public Files but {doc.attached_to_doctype} is Not "
                                 f"Mentioned in Rohit Settings.\nKindly Mention {doc.attached_to_doctype} to "
                                 f"Create a Public File with this Doctype or Make this File Private")
        else:
            if doc_allowed != 1:
                frappe.throw(f"{doc.file_name} is a Public File and You are Not Allowed to Create Public Files. Kindly "
                             f"make this file Private and Proceed")


def check_file_availability(file_doc):
    # Validate File available on Server
    full_path = File.get_full_path(file_doc)
    if os.path.exists(full_path):
        file_doc.file_available_on_server = 1
    else:
        file_doc.file_available_on_server = 0
        frappe.msgprint(f"{file_doc.file_name} is Not Available on Server")
