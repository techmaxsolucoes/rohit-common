# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document


class RohitSettings(Document):
    def validate(self):
        self.sort_single_field_child("roles_allow_pub_att", "role")
        self.sort_single_field_child("docs_with_pub_att", "document_type")
        self.sort_single_field_child("auto_convert_pub_priv", "document_type")

    def sort_single_field_child(self, table_name, field_name):
        sorted_table = []
        row_dict = {}
        for row in self.get(table_name):
            row_dict[field_name] = row.get(field_name)

            sorted_table.append(row_dict.copy())
        sorted_table = sorted(sorted_table, key=lambda i: i[field_name], reverse=0)
        self.set(table_name, [])
        for d in sorted_table:
            self.append(table_name, d)
