# Copyright (c) 2013, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from ....utils.rohit_common_utils import get_folder_details


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    if filters.get("summary_dt") == 1:
        return ["Attached to Doctype::300", "No of Files:Int:100", "Size (MB):Float:100"]
    elif filters.get("summary_fol") == 1:
        return ["Attached to Doctype::300", "No of Files:Int:100", "Size (MB):Float:100"]
    else:
        if filters.get("is_folder") == 1:
            return [
                "ID:Link/File:450", "File Name::200", "Parent Folder::350", "Size(MB):Float:100",
                "Left:Int:80", "Right:Int:80", "Files:Int:80","Is Home:Int:40", "Is Attachment::40"
            ]
        else:
            return [
                "ID:Link/File:150", "File Name::200",
                {
                    "label": "Attached To DT",
                    "fieldname": "attached_to_dt",
                    "width": 100
                },
                {
                    "label": "Attached to Name",
                    "fieldname": "attached_to_name",
                    "fieldtype": "Dynamic Link",
                    "options": "attached_to_dt",
                    "width": 100
                },
                "Available:Int:50", "Size(kB):Float:100", "Left:Int:80", "Right:Int:80", "Parent Folder::350",
                "Private:Int:40", "Imp:Int:40", "Del:Int:40", "Owner::150", "Created On:Datetime:150", "URL::300"
            ]


def get_data(filters):
    conditions, cond_summary = get_conditions(filters)
    if filters.get("summary_dt") == 1:
        data = frappe.db.sql("""SELECT IFNULL(attached_to_doctype, "NO DOCTYPE"), COUNT(name) as no_of_files, 
        ROUND(((SUM(file_size))/1024/1024),2) FROM `tabFile` WHERE docstatus=0 AND is_folder=0 %s
        GROUP BY attached_to_doctype ORDER BY no_of_files DESC """ % cond_summary, as_list=1)
    elif filters.get("summary_fol") == 1:
        data = frappe.db.sql("""SELECT IFNULL(folder, "NO FOLDER"), COUNT(name) as no_of_files,
            ROUND(((SUM(file_size))/1024/1024),2)
            FROM `tabFile`
            WHERE docstatus=0 AND is_folder=0 
            GROUP BY folder ORDER BY no_of_files DESC """, as_list=1)
    else:
        if filters.get("is_folder") == 1:
            data = frappe.db.sql("""SELECT name, file_name, folder, ROUND(file_size/1024/1024,2), lft, rgt, (rgt - lft),
                is_home_folder, is_attachments_folder
                FROM `tabFile` WHERE docstatus = 0 %s ORDER BY lft, rgt""" % (conditions), as_list=1)
        else:
            query = """SELECT name, IFNULL(file_name, "NO NAME"), IFNULL(attached_to_doctype, "NO DOCTYPE"), 
                IFNULL(attached_to_name,"NO DOCNAME"), file_available_on_server,
                ROUND(file_size/1024,2), lft, rgt, IFNULL(folder, "NO FOLDER"), is_private, 
                important_document_for_archive, mark_for_deletion, owner, creation, file_url
                FROM `tabFile` WHERE docstatus=0 %s ORDER BY creation""" % (conditions)
            data = frappe.db.sql(query, as_list=1)

    return data


def get_conditions(filters):
    conditions = ""
    cond_summary = ""
    if filters.get("is_folder") == 1:
        conditions += " AND is_folder=1"
    else:
        conditions += " AND is_folder=0"

    if filters.get("private") == "Only Private":
        conditions += " AND is_private=1"
        cond_summary += " AND is_private=1"
    elif filters.get("private") == "Only Public":
        conditions += " AND is_private=0"
        cond_summary += " AND is_private=0"
    else:
        pass

    if filters.get("dt_types") != "None" and filters.get("doctype"):
        conditions += " AND attached_to_doctype = '%s'" % (filters.get("doctype"))
    elif filters.get("dt_types") == "None" and filters.get("doctype"):
        frappe.throw("None Doctype Selected and hence Cannot Select a Specific Doctype")

    if filters.get("dt_types") == "None":
        conditions += " AND attached_to_doctype IS NULL"

    if filters.get("folder"):
        folder_details = get_folder_details(filters.get("folder"))
        lft = folder_details[0].lft + 1
        rgt = folder_details[0].rgt - 1
        conditions += " AND lft >= %s AND rgt <= %s" % (lft, rgt)

    if filters.get("no_parent") == 1:
        conditions += " AND folder IS NULL"

    if filters.get("on_server") == "Yes":
        conditions += " AND file_available_on_server = 1"
        cond_summary += " AND file_available_on_server = 1"
    elif filters.get("on_server") == "No":
        conditions += " AND file_available_on_server = 0"
        cond_summary += " AND file_available_on_server = 0"

    if filters.get("deletion"):
        cond_summary += " AND mark_for_deletion = 1"
        conditions += " AND mark_for_deletion = 1"

    if filters.get("archive"):
        cond_summary += " AND important_document_for_archive = 1"
        conditions += " AND important_document_for_archive = 1"

    return conditions, cond_summary
