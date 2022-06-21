# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def execute():
    autonamed_assets = frappe.db.sql("""SELECT name, autoname, get_automatic_name
        FROM `tabAsset` WHERE autoname=1 AND get_automatic_name = 0""", as_dict=1)
    for ass in autonamed_assets:
        frappe.db.set_value("Asset", ass.name, "get_automatic_name", 1)
