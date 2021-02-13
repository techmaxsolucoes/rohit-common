#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
import time
from datetime import date
from frappe.utils import flt, getdate
from frappe.utils.background_jobs import enqueue
from ..validations.address import validate_gstin_from_portal


def enqueue_gstin_update():
    enqueue(execute, queue="long", timeout=7200)


def execute():
    st_time = time.time()
    validate = 0
    auto_days = flt(frappe.get_value("Rohit Settings", "Rohit Settings", "auto_validate_gstin_after"))
    add_list = frappe.db.sql("""SELECT name, validated_gstin, gst_validation_date FROM `tabAddress`
    WHERE validated_gstin IS NOT NULL AND gst_status != 'Cancelled' ORDER BY gst_validation_date, name""", as_dict=1)
    for add in add_list:
        changes_made = 0
        if add.gst_validation_date:
            days_since_validation = (date.today() - getdate(add.gst_validation_date)).days
            if days_since_validation > auto_days:
                # Now Validate the GSTIN
                add_doc = frappe.get_doc("Address", add.name)
                validate_gstin_from_portal(add_doc)
                changes_made = 1
                validate += 1
        else:
            changes_made = 1
            add_doc = frappe.get_doc("Address", add.name)
            validate_gstin_from_portal(add_doc)
            validate += 1
        if changes_made == 1:
            try:
                add_doc.flags.ignore_mandatory = True
                add_doc.save()
                print(f"{add_doc.name} Saved")
            except Exception as e:
                print(f"{e}")
        if validate % 50 == 0 and validate > 0:
            print(f"Committing Changes after {validate} Changes. Time Elapsed = {int(time.time() - st_time)} seconds")
            time.sleep(2)
            frappe.db.commit()
    print(f"Total GSTIN validated from GSTIN Website {validate}")
    print(f"Total Time Taken = {int(time.time() - st_time)} seconds")
