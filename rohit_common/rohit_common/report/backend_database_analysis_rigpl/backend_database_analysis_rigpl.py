#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model import core_doctypes_list
from ....patches.backend_table_analysis import get_size_of_all_tables, get_columns_of_all_tables


def execute(filters=None):
    """
    Executes a report
    """
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    """
    Returns the columns for the Report
    """
    get_conditions(filters)
    cols = ""
    if filters.get("all_tables") == 1:
        cols = [
            "Database Name::200", "Table Name::400",
            "Size in MB:Float:100", "Data MB::100", "Index MB::100", "Total Row:Int:150"
        ]
    elif filters.get("unused_tables") == 1:
        cols = [
            "DB Name::200", "App Name::100", "Module Name::100", "Table Name::200",
            "DT Name:Link/DocType:200", "Size in MB:Float:100", "Data MB::100",
            "Last Entry:Datetime:200", "Total Row:Int:150"
        ]
    else:
        cols = [
            "Database Name::200", "Table Name::400", "Total Columns:Int:150"
        ]
    return cols


def get_data(filters):
    """
    Returns the data in list format for the report
    """
    data = []
    if filters.get("all_tables") == 1:
        data_dict = get_size_of_all_tables()
        for drow in data_dict:
            row = [
                drow.db_name, drow.tbl_name, drow.size_mb,
                drow.dl_mb, drow.ind_mb, drow.tbl_rows, drow.no_of_cols
            ]
            data.append(row)
    elif filters.get("unused_tables") == 1:
        data_dict = get_size_of_all_tables()
        dt_fds = {"name", "modified", "issingle",
                  "istable", "module", "app", "is_virtual"}
        virtual_dts = frappe.get_list(
            "DocType", fields=dt_fds, filters={"is_virtual": 1})
        single_dts = frappe.get_list(
            "DocType", fields=dt_fds, filters={"issingle": 1})
        all_dts = frappe.db.sql("""SELECT name, modified, issingle, istable, module, app, is_virtual
            FROM `tabDocType`""", as_dict=1)
        # frappe.throw(str(all_dts))
        core_dts = core_doctypes_list
        installed_apps = frappe.get_installed_apps()
        # frappe.throw(str(installed_apps))
        # To check if a Table is there in DB but not in any app we need to check the following
        # 1. Table should not be default fields, get installed_apps, get_dts_from_installed_apps
        for dty in core_dts:
            # mdty = frappe.get_meta(dty)
            print(dty)

        for drow in data_dict:
            row = [
                drow.db_name, "app", "module", drow.tbl_name, "dt",
                drow.size_mb, drow.dl_mb, drow.ind_mb, drow.tbl_rows, drow.no_of_cols
            ]
            data.append(row)
    else:
        data_dict = get_columns_of_all_tables()
        for drow in data_dict:
            row = [
                drow.db_name, drow.tbl_name, drow.no_of_cols
            ]
            data.append(row)
    return data


def get_conditions(filters):
    """
    To get condiitons from filters
    """
    chk_bx = flt(filters.get("all_tables")) + \
        flt(filters.get("col_nos")) + flt(filters.get("unused_tables"))
    if chk_bx > 1 or chk_bx == 0:
        frappe.throw("Only 1 Checkbox is Allowed at a Time")
