#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
import frappe


def update_child_table(doc, table_name, row_list):
    for data in row_list:
        data = frappe._dict(data)
        doc.append(table_name, data.copy())
