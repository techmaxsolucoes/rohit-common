# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

# This is the Test to run if update address is working from google or not
from __future__ import unicode_literals
import frappe
from ..validations.google_maps import geocoding

def execute():
    add_doc_name = input("Please Enter the Exact name of the Address for which Google Data is needed: ")
    add_doc = frappe.get_doc('Address', add_doc_name)
    geocoding(add_doc)
    print('Document {} Updated with JSON {}'.format(add_doc.name, add_doc.json_reply))