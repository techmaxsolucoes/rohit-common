# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import ast
from difflib import SequenceMatcher as sm
from ..rohit_common.india_gst_api.gst_public_api import search_gstin


def execute():
    add_with_gstin = frappe.db.sql("""SELECT name, gstin, address_title, validated_gstin, gstin_json_reply 
        FROM `tabAddress` WHERE gstin != 'NA' AND gstin IS NOT NULL ORDER BY name""", as_dict=1)
    get_gstin_json(add_with_gstin)
    update_addresses_from_gstin_json(add_with_gstin)


def get_gstin_json(add_dict):
    updated_addresses = 0
    for add in add_dict:
        add_doc = frappe.get_doc("Address", add.name)
        if add.gstin and add.gstin != "NA":
            if not add.validated_gstin:
                print("Updating Address {}".format(add_doc.name))
                gstin_json = search_gstin(add.gstin)
                if gstin_json.get('status_cd', 1) == 1:
                    updated_addresses += 1
                    frappe.db.set_value("Address", add.name, "gstin_json_reply", str(gstin_json))
                    frappe.db.set_value("Address", add.name, "validated_gstin", gstin_json.get("gstin"))
                    frappe.db.set_value("Address", add.name, "gst_status", gstin_json.get("sts"))
                    add_doc.reload()
                else:
                    print("Error in GST JSON")
        if updated_addresses % 20 == 0 and updated_addresses > 0:
            frappe.db.commit()
            print("Committing Changes")
    print("Total Addresses Updated with GST JSON = {}".format(updated_addresses))


def update_addresses_from_gstin_json(add_dict):
    valid_gstin = 0
    invalid_gstin = 0
    update_frm_trd_name = 0
    update_frm_lgl_name = 0
    not_updating = 0
    for add in add_dict:
        if add.validated_gstin:
            if add.gstin == add.validated_gstin:
                valid_gstin += 1
                gst_json = ast.literal_eval(add.gstin_json_reply)
                if gst_json.get("status_cd", 1) == 1:
                    # Now Check the Legal Name lgnm and Also another field is Trade Name (tradeNam)
                    lgl_name = gst_json.get("lgnm")
                    trd_name = gst_json.get("tradeNam")
                    lgl_ratio = sm(lambda x:x in (" ", ".", ","), (add.address_title).lower(), lgl_name.lower()).ratio()
                    trd_ratio = sm(None, (add.address_title).lower(), trd_name.lower()).ratio()
                    if lgl_ratio > 0.6:
                        update_frm_lgl_name += 1
                        frappe.db.set_value("Address", add.name, "address_title", lgl_name)
                        print("Updated with Legal Name")
                    elif trd_ratio > 0.6:
                        update_frm_trd_name += 1
                        frappe.db.set_value("Address", add.name, "address_title", trd_name)
                        print("Updated with Trade Name")
                    else:
                        not_updating += 1
                        print("Not Updating {}, Legal Ratio= {} and Trade Ratio= {}".
                              format(add.name, lgl_ratio, trd_ratio))
                else:
                    print("Status NOT 1")
            else:
                invalid_gstin += 1
        # print("{} GSTIN: {} and Title: {}".format(add.name, add.gstin, add.address_title))
    print("Total Addresses with GSTIN = {}".format(len(add_dict)))
    print("Total Address with Validated GSTIN = {}".format(valid_gstin))
    print("Total Address with Invalid GSTIN = {}".format(invalid_gstin))
    print("Total Updated from Legal Name = {}".format(update_frm_lgl_name))
    print("Total Updated from Trade Name = {}".format(update_frm_trd_name))
    print("Total Updated Titles {}".format(update_frm_trd_name + update_frm_lgl_name))
    print("Total Not Updated = {}".format(not_updating))
