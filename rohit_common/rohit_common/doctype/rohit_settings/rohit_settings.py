# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe.model.document import Document


class RohitSettings(Document):
    def validate(self):
        min_days_to_keep = 30
        self.sort_single_field_child("auto_deletion_policy_for_files", "document_type")
        self.sort_single_field_child("roles_allow_pub_att", "role")
        self.sort_single_field_child("docs_with_pub_att", "document_type")
        self.sort_single_field_child("auto_delete_from_version", "document_type")
        self.sort_single_field_child("bg_submit_cancel_docs", "document_type")
        for d in self.auto_deletion_policy_for_files:
            if flt(d.days_to_keep) < min_days_to_keep:
                frappe.throw(f"Minimum {min_days_to_keep} Days is Needed to Keep Files")

    def sort_single_field_child(self, table_name, field_name):
        sorted_table = []
        row_dict = {}
        idx = 1
        for row in self.get(table_name):
            print(row.__dict__)
            row_dict = row.__dict__
            del(row_dict["idx"])
            sorted_table.append(row_dict.copy())
        sorted_table = sorted(sorted_table, key=lambda i: i[field_name], reverse=0)
        self.set(table_name, [])
        for d in sorted_table:
            d["idx"] = idx
            idx += 1
            self.append(table_name, d)
