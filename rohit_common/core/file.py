# Copyright (c) 2022 Rohit Industries Group Private Limited and Contributors.
# For license information, please see license.txt
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr


@frappe.whitelist()
def get_files_by_search_text(text):
    """
    This function seems similar to the one by frappe but here is a big difference
    Here if you do add a field in customized form view to the search then you can
    search the files by that fields as well so here the docname of the attached field
    when entered in the customize form view in search fields wee can easily
    search the files.
    """
    file_meta = frappe.get_meta(doctype="File")
    search_flds = file_meta.get_search_fields()
    std_flds = ["name", "file_name", "file_url", "modified"]
    if not text:
        return []
    text = "%" + cstr(text).lower() + "%"
    for fld in search_flds:
        if fld not in std_flds:
            std_flds.append(fld)
    or_filters = []
    for fld in search_flds:
        or_filters.append([f"{fld}", "LIKE", f"{text}"])
    fl_lst = frappe.db.get_list(doctype="File", fields=search_flds,
                                filters={"is_folder": 0},
                                or_filters=or_filters, order_by="modified")
    return fl_lst
