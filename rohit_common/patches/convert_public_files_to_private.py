# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import frappe
from ..rohit_common.validations.file import check_file_availability, delete_file_dt
from frappe.utils.nestedset import rebuild_tree


def execute():
    # First Part is to Convert Existing Public Files to Private files as defined in Rohit Settings
    # If a doc type is not defined in Rohit Settings then all files attached to that doc type are converted to Private
    # For files not attached to any doc type the file is just checked for availability on server and if not then deleted

    st_time = time.time()
    tot_files = frappe.get_all("File")
    print(f"Total Files in DB = {len(tot_files)}")
    public_file_list = frappe.db.sql("""SELECT name, attached_to_doctype FROM `tabFile` WHERE is_private = 0 
    AND is_folder = 0""", as_dict=1)
    print(f"Total Public Files in Database {len(public_file_list)}")
    time.sleep(1)
    sno = 1
    changes_done = 0
    roset = frappe.get_single("Rohit Settings")
    allowed_dt = []
    deleted_files_list = []
    deleted_files_count = 0
    for d in roset.docs_with_pub_att:
        allowed_dt.append(d.document_type)
    for file in public_file_list:
        # print(f"Checking {file.name}")
        fd = frappe.get_doc("File", file.name)
        file_available = check_file_availability(fd)
        if file_available == 1:
            old_private = fd.is_private
            old_avail = fd.file_available_on_server
            if fd.attached_to_doctype not in allowed_dt:
                # print(f"{sno}. Processing {file.name} Attached to {fd.attached_to_doctype}: {fd.attached_to_name}")
                if file_available == 1:
                    frappe.db.set_value("File", fd.name, "file_available_on_server", 1)
                    new_avail = 1
                    new_private = fd.is_private
                    if old_avail != new_avail or old_private != new_private:
                        changes_done += 1
                    sno += 1
        else:
            # Delete the file in DB
            comments = f"Removed {file.name} as Not Available on Server"
            deleted_files_list.append(file.name)
            deleted_files_count += 1
            changes_done += 1
            delete_file_dt(fd=fd, comment=comments)
        if changes_done % 500 == 0 and changes_done != 0:
            print(f"Saving Changes to Database after {changes_done} Changes")
            frappe.db.commit()
    pub_time = int(time.time() - st_time)
    print(f"Total Time Taken to Convert Public Files to Private {pub_time} seconds")
    frappe.db.commit()

    # Second Part is to check the files Not Attached to Any Doc Type and if not available on server they are deleted.
    no_dt_files = frappe.db.sql("""SELECT name FROM `tabFile` WHERE attached_to_doctype IS NULL 
    AND is_folder = 0""", as_dict=1)
    changes_done = 0
    for file in no_dt_files:
        fd = frappe.get_doc("File", file.name)
        file_available = check_file_availability(fd)
        if file_available == 1:
            if fd.file_available_on_server != 1:
                frappe.db.set_value("File", fd.name, "file_available_on_server", 1)
        else:
            comments = f"Removed {file.name} as Not Available on Server"
            delete_file_dt(fd=fd, comment=comments)
            deleted_files_list.append(file.name)
            deleted_files_count += 1
        if changes_done % 500 == 0 and changes_done != 0:
            print(f"Saving Changes to Database after {changes_done} Changes")
            frappe.db.commit()

    # Third Part is to Move Files without any Folder or Attached to Home Folder into Attachments Folder if they exist
    home_fold = frappe.db.sql("""SELECT name FROM `tabFile` WHERE is_home_folder = 1""", as_list=1)
    att_fold = frappe.db.sql("""SELECT name FROM `tabFile` WHERE is_attachments_folder = 1""", as_list=1)
    att_fold = att_fold[0][0]
    home_fold = home_fold[0][0]

    no_folder_files = frappe.db.sql("""SELECT name, folder FROM `tabFile` WHERE folder IS NULL 
    AND is_folder=0""", as_dict=1)

    files_in_home = frappe.db.sql("""SELECT name, folder FROM `tabFile` WHERE folder = '%s' 
    AND is_folder=0""" % home_fold, as_dict=1)

    print(f"Total Files Without Folder = {len(no_folder_files)}")
    time.sleep(1)
    changes_done = 0
    for file in no_folder_files:
        fd = frappe.get_doc("File", file.name)
        file_available = check_file_availability(fd)
        if file_available == 1:
            fd.folder = att_fold
            fd.save()
            changes_done += 1
        else:
            comments = f"Removed {file.name} as Not Available on Server"
            delete_file_dt(fd=fd, comment=comments)
            deleted_files_list.append(file.name)
            deleted_files_count += 1
        if changes_done%500 == 0 and changes_done !=0:
            print(f"Saving Changes to Database after {changes_done} Changes")
            frappe.db.commit()
    for file in files_in_home:
        fd = frappe.get_doc("File", file.name)
        file_available = check_file_availability(fd)
        if file_available == 1:
            fd.folder = att_fold
            fd.save()
            changes_done += 1
        else:
            comments = f"Removed {file.name} as Not Available on Server"
            delete_file_dt(fd=fd, comment=comments)
            deleted_files_list.append(file.name)
            deleted_files_count += 1
        if changes_done%500 == 0 and changes_done !=0:
            print(f"Saving Changes to Database after {changes_done} Changes. "
                  f"Total Time Elapsed = {int(time.time() - st_time)}")
            frappe.db.commit()
    frappe.db.commit()
    fold_time = int(time.time() - st_time - pub_time)
    print(f"Total Time Take for Changing Folder = {fold_time} seconds")
    time.sleep(1)
    # Next Make the Changes in Tree Structure if needed
    rebuild_tree("File", "folder")
    nest_time = int(time.time() - st_time - pub_time - fold_time)

    # Next Recaclulated the Folder Size

    tot_time = int(time.time() - st_time)
    print(deleted_files_list)
    print(f"Total Files Deleted Due to Unavailable on Server = {len(deleted_files_list)}")
    print(f"Total Time Taken for Nested Folder Restructuring = {nest_time} seconds")
    print(f"Total Time Taken {tot_time} seconds")
