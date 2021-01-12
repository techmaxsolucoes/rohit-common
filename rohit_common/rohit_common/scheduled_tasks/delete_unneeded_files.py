# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Group Pvt Ltd. and contributors
# For license information, please see license.txt

# This Scheduled Tasks Would check all files marked for Deletion and Delete them.
# It would also check the files which are attached to some doctypes which need to be deleted as per deletion policy

from __future__ import unicode_literals
import os
import time
import frappe
from ...utils.rohit_common_utils import make_file_path
from ..validations.file import check_file_availability


def execute():
    st_time = time.time()
    print("Checking for Files Marked to Delete")
    time.sleep(1)
    files_marked_to_delete = frappe.db.sql("""SELECT name, file_name, file_url, attached_to_doctype, attached_to_name 
    FROM `tabFile` WHERE mark_for_deletion = 1""", as_dict=1)
    for file in files_marked_to_delete:
        fd = frappe.get_doc("File", file.name)
        # Check if File URL not in another File so don't delete
        other_file = frappe.db.sql("""SELECT name FROM `tabFile` WHERE file_url = '%s'""" % fd.file_url)
        if other_file:
            file_exists_in_others_as_well = 1
        else:
            file_exists_in_others_as_well = 0
        file_path = make_file_path(fd)
        if file.attached_to_doctype and file.attached_to_name:
            doc = frappe.get_doc(file.attached_to_doctype, file.attached_to_name)
            ignore_permissions = doc.has_permission("write") or False
            if frappe.flags.in_web_form:
                ignore_permissions = True
            comment = doc.add_comment("Attachment Removed", f"Removed {file.name} as it Was Marked for Deletion")
        else:
            ignore_permissions = True
        file_available = check_file_availability(fd)
        if file_available == 1 and file_exists_in_others_as_well == 0:
            os.remove(file_path)
        frappe.delete_doc("File", file.name, ignore_permissions=ignore_permissions)
    frappe.db.commit()
    mark_time = int(time.time() - st_time)

    # Now check the Doctypes in Settings for Auto Deletion Rule
    print("Checking for Auto Deletion of Files")
    time.sleep(1)
    ro_set = frappe.get_single("Rohit Settings")
    tot_auto_delete = 0
    archive_files = 0
    for row in ro_set.auto_deletion_policy_for_files:
        dt_conds = ""
        if row.doctype_conditions:
            dt_conds = " AND %s" % row.doctype_conditions
        query = """SELECT fd.name FROM `tabFile` fd, `tab%s` dt WHERE fd.attached_to_doctype = '%s' AND
        fd.creation <= DATE_SUB(NOW(), INTERVAL %s DAY) AND dt.name = fd.attached_to_name %s"""\
                % (row.document_type, row.document_type, row.days_to_keep, dt_conds)
        files = frappe.db.sql(query, as_dict=1)
        tot_auto_delete += len(files)
        for file in files:
            fd = frappe.get_doc("File", file.name)
            doc = frappe.get_doc(row.document_type, fd.attached_to_name)
            # print(f"Checking {fd.name} Attached To: {fd.attached_to_doctype}: {fd.attached_to_name}")
            file_path = make_file_path(fd)
            if fd.important_document_for_archive != 1:
                print(f"Removed File {file.name} Attached to {row.document_type}: {fd.attached_to_name}")
                doc.add_comment("Attachment Removed", f"Removed {file.name} Due to Deletion Policy to Delete After "
                                                      f"{row.days_to_keep} Days")
                file_available = check_file_availability(fd)
                if file_available == 1:
                    os.remove(file_path)
                frappe.delete_doc("File", file.name, ignore_permissions=1)
            else:
                archive_files += 1
    frappe.db.commit()
    del_time = int(time.time() - st_time)

    # Lastly Check all files in DB which are not Marked as Available on Server and Delete those files
    print("Check for File Availability and Updating the Same")
    time.sleep(1)
    avail_count = 0
    non_validated_files = frappe.db.sql("""SELECT name FROM `tabFile` WHERE file_available_on_server = 0 
    AND is_folder=0""", as_dict=1)
    print(f"Total Non Available Files = {len(non_validated_files)}")
    for file in non_validated_files:
        # print(f"Checking {file.name}")
        fd = frappe.get_doc("File", file.name)
        file_available = check_file_availability(fd)
        if file_available == 1:
            fd.file_available_on_server = 1
            fd.save()
            avail_count += 1
        else:
            frappe.delete_doc("File", fd.name, ignore_permissions=1)
        if avail_count % 500 == 0 and avail_count > 0:
            frappe.db.commit()
            print(f"Committing Changes after {avail_count} files made available")
    avail_time = int(time.time() - st_time)

    tot_time = int(time.time() - st_time)
    print(f"Total Marked Files Deleted = {len(files_marked_to_delete)}")
    print(f"Total Time Taken for Marked Files Deletion = {mark_time} seconds")
    print(f"Total Auto Files Deleted = {tot_auto_delete - archive_files}")
    print(f"Total Auto Files Deleted in Archive = {archive_files}")
    print(f"Total Time Taken for Auto Deletion of Files {del_time - mark_time} seconds")
    print(f"Total No of Files Made Available = {avail_count}")
    print(f"Total Time Take for Making Files Available = {avail_time - mark_time}")
    print(f"Total Time Taken {tot_time} seconds")
