# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import frappe
from frappe.utils import get_site_base_path
from frappe.core.doctype.file.file import get_content_hash
from pathlib import Path


def on_trash(doc, method):
    if doc.important_document_for_archive == 1:
        frappe.throw(f"{doc.name} is Checked for Archive hence Cannot be Deleted")


def validate(doc, method):
    # check_file_name(doc)
    check_file_availability(doc)
    get_size(doc)
    if doc.mark_for_deletion == 1 and doc.important_document_for_archive == 1:
        frappe.throw(f"{doc.name} Cannot be Marked for Deletion as its an Important Document")
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


def get_size(doc):
    file_path = get_file_path_from_doc(doc)
    if doc.file_available_on_server == 1:
        if Path(file_path).stat().st_size != doc.file_size:
            doc.file_size = Path(file_path).stat().st_size
    '''
    doc.flags.ignore_permissions = True
    if doc.is_folder == 1:
        files = frappe.db.sql("""SELECT name, size FROM `tabFile` WHERE lft > %s 
        AND rgt < %s""" % (doc.lft, doc.rgt), as_dict=1)
        print(files)
    '''


def check_file_name(file_doc):
    disallowed_chars = ["'", '"']
    for d in disallowed_chars:
        if d in file_doc.file_name:
            frappe.throw(f"Illegal Character in File Name {file_doc.file_name}. "
                         "Please change and remove the illegal character from the file name to Proceed.")


def check_file_availability(file_doc, backend=0):
    # Validate File available on Server
    full_path = get_file_path_from_doc(file_doc)
    if file_doc.is_folder != 1:
        if os.path.exists(full_path):
            file_doc.file_available_on_server = 1
            if backend == 1:
                print(f"{file_doc.name} is Available on Server and Status Updated")
            return 1
        else:
            # File is not existing check if its in Private Folder with same name and content hash then change the
            # link for the link and update
            if file_doc.is_private != 1:
                if file_doc.file_name:
                    new_file_url = "/private/files/" + file_doc.file_name
                    full_path = get_site_base_path() + new_file_url
                    if os.path.exists(full_path):
                        # Check the content hash
                        with open(full_path, "rb") as f:
                            new_hash = get_content_hash(f.read())
                            if new_hash == file_doc.content_hash:
                                print(f"File {file_doc.name} Found in Private Files hence Changing")
                                frappe.db.set_value("File", file_doc.name, "is_private", 1)
                                frappe.db.set_value("File", file_doc.name, "file_url", new_file_url)
                                frappe.db.set_value("File", file_doc.name, "file_available_on_server", 1)
                                frappe.db.commit()
                                return 1
                            else:
                                file_doc.file_available_on_server = 0
                                if backend == 0:
                                    frappe.msgprint(f"{file_doc.file_name} is Not Available on Server")
                                else:
                                    return 0
                    else:
                        file_doc.file_available_on_server = 0
                        return 0


def get_file_path_from_doc(file_doc):
    if file_doc.file_url:
        if "http" in file_doc.file_url:
            file_name = (file_doc.file_url).rsplit("/", 1)[-1]
            # Check file_name in Both Public and Private files and if found change the URL and File Name
            file_in_private = file_name_exists(file_name, is_private=1)
            if file_in_private == 1:
                file_url = "/private/files/" + file_name
                frappe.db.set_value("File", file_doc.name, "is_private", 1)
                frappe.db.set_value("File", file_doc.name, "file_url", file_url)
                frappe.db.set_value("File", file_doc.name, "file_name", file_name)
                frappe.db.commit()
            else:
                file_in_public = file_name_exists(file_name)
                if file_in_public == 1:
                    file_url = "/files/" + file_name
                    frappe.db.set_value("File", file_doc.name, "is_private", 0)
                    frappe.db.set_value("File", file_doc.name, "file_url", file_url)
                    frappe.db.set_value("File", file_doc.name, "file_name", file_name)
                    frappe.db.commit()
        elif file_doc.file_url[0] != "/":
            file_url = "/" + file_doc.file_url
            frappe.db.set_value("File", file_doc.name, "file_url", file_url)
            frappe.db.commit()
        if file_doc.is_private == 1:
            full_path = get_site_base_path() + file_doc.file_url
        else:
            full_path = get_site_base_path() + "/public" + file_doc.file_url
    else:
        # Assumes if there is no file URL then it would be the file URL in File Name
        full_path = get_site_base_path() + file_doc.file_name
    return full_path


def check_other_files_with_same_file(fd):
    if fd.file_url:
        other_file = frappe.db.sql("""SELECT name FROM `tabFile` WHERE file_url = '%s' AND name != '%s'""" %
                                   (fd.file_url, fd.name))
        if other_file:
            return 1
        else:
            if fd.file_name:
                url_like = "%" + fd.file_name + "%"
                other_file = frappe.db.sql("""SELECT name FROM `tabFile` WHERE file_url LIKE '%s' AND name != '%s'"""
                                           % (url_like, fd.name))
                if other_file:
                    return 1
                else:
                    return 0
            else:
                return 0


def file_name_exists(file_name, is_private=0):
    if is_private == 1:
        full_path = get_site_base_path() + "/private/files/" + file_name
    else:
        full_path = get_site_base_path() + "/public/files/" + file_name

    if os.path.exists(full_path):
        return 1
    else:
        return 0


def delete_file_dt(fd, comment=None):
    # fd = File doctype
    if fd.important_document_for_archive == 1:
        # Don't delete Files which are marked for archives
        pass
    else:
        # Check if File Available on server basically search for file name in Private and Public Files
        # if Found then change the link also check if file is there in another file data
        if fd.file_available_on_server == 1:
            # File available on Server and now check if the file is not present in another file databases
            other_files = check_other_files_with_same_file(fd)
            if other_files == 1:
                # Delete only the File Doc and not the actual file
                print(f"Only Deleting the File Doc {fd.name} and not the Actual File")
                delete_only_file_doc(fd, comment=comment)
            else:
                # Delete the file doc and also the actual file on the server
                print(f"Deleting the File Doc {fd.name} and Also the File")
                delete_only_file_doc(fd, comment=comment)
                full_path = get_file_path_from_doc(fd)
                try:
                    os.remove(path=full_path)
                except:
                    print(f"Unable to Remove the Actual File at {full_path}")
        else:
            file_available = check_file_availability(fd)
            if file_available == 1:
                fd.file_available_on_server = 1
                other_files = check_other_files_with_same_file(fd)
                if other_files:
                    print(f"Only Deleting the File Doc {fd.name} and not the Actual File Found in 2nd Attempt")
                    delete_only_file_doc(fd, comment=comment)
                else:
                    print(f"Deleting the File Doc {fd.name} and Also the File")
                    delete_only_file_doc(fd, comment=comment)
                    full_path = get_file_path_from_doc(fd)
                    os.remove(path=full_path)
            else:
                delete_only_file_doc(fd, comment=comment)


def delete_only_file_doc(fd, comment=None):
    if fd.attached_to_doctype and fd.attached_to_name and comment is not None:
        dt = frappe.get_doc(fd.attached_to_doctype, fd.attached_to_name)
        dt.add_comment("Attachment Removed", comment)
    frappe.delete_doc("File", fd.name, for_reload=1, ignore_permissions=1)
