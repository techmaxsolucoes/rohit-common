#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
import re
import ast
from datetime import date
from frappe.utils import flt, getdate
from difflib import SequenceMatcher as sm
from .google_maps import geocoding, render_gmap_json
from ..india_gst_api.gst_public_api import search_gstin
from rohit_common.utils.rohit_common_utils import replace_java_chars, validate_email_addresses


def validate(doc, method):
    if not doc.flags.ignore_mandatory:
        country_validation(doc)
        gstin_validation(doc)
        geocode(doc, method)
        if doc.email_address_validated != 1:
            valid_email = validate_email_addresses(doc.email_id)
            doc.email_address_validated = valid_email
    validate_primary_address(doc, method)
    validate_shipping_address(doc, method)


def gstin_validation(doc):
    if doc.gstin:
        if doc.gstin != "NA":
            if len(doc.gstin) != 15:
                frappe.msgprint("GSTIN should be exactly as 15 digits or NA", raise_exception=1)
            else:
                valid_chars_gstin = "0123456789ABCDEFGIHJKLMNOPQRSTUVYWXZ"
                for n, char in enumerate(reversed(doc.gstin)):
                    if not valid_chars_gstin.count(char):
                        frappe.msgprint("Only Numbers and alphabets in UPPERCASE are allowed in GSTIN or NA",
                                        raise_exception=1)
                if doc.state_rigpl:
                    state = frappe.get_doc("State", doc.state_rigpl)
                else:
                    frappe.throw("Selected State is NOT Valid for {0}".format(doc.state_rigpl))
                if doc.gstin[:2] != state.state_code_numeric:
                    # fetch and update the state automatically else throw error
                    state_from_gst = frappe.db.sql("""SELECT name FROM `tabState` 
                    WHERE state_code_numeric = '%s'""" % (doc.gstin[:2]), as_list=1)
                    if state_from_gst:
                        doc.state_rigpl = state_from_gst[0][0]
                        doc.gst_state = state_from_gst[0][0]
                        doc.state = state_from_gst[0][0]
                    else:
                        frappe.throw("State Selected {0} for Address {1}, GSTIN number should begin with {2}".
                                     format(doc.state_rigpl, doc.name, state.state_code_numeric))
                validate_gstin_from_portal(doc)
            doc.pan = doc.gstin[2:12]
        else:
            doc.pan = ""
            doc.validated_gstin = ""
            doc.gstin_json_reply = ""
            doc.gst_status = ""
    else:
        if doc.country == 'India':
            frappe.throw('GSTIN Mandatory for Indian Addresses or Enter NA for NO GSTIN')


def country_validation(doc):
    doc.pincode = re.sub('[^A-Za-z0-9]+', '', str(doc.pincode))
    if doc.country:
        country_doc = frappe.get_doc("Country", doc.country)
        if country_doc.gst_details != 1:
            doc.gstin = 'NA'
            doc.gst_state = ""
            doc.gst_state_number = ""

        if country_doc.known_states == 1:
            # Country has known states means state doctype should have states for that country
            state_list = frappe.db.sql("""SELECT name FROM `tabState` WHERE country = '%s'""" % doc.country, as_dict=1)
            if state_list:
                if doc.state_rigpl is None or not doc.state_rigpl or doc.state_rigpl == "":
                    frappe.throw('State RIGPL for Country {} is Mandatory in Address {}'.format(doc.country, doc.name))
                if country_doc.pincode_length:
                    pincode_length = replace_java_chars(country_doc.pincode_length)
                    if 'or' in pincode_length:
                        pc_length = pincode_length.split("or")
                    else:
                        pc_length = [pincode_length]
                    pincode_pass = 0
                    for d in pc_length:
                        if len(doc.pincode) == flt(d):
                            pincode_pass = 1
                    if pincode_pass != 1:
                        frappe.throw("For Address {}: Pincode should be {} Digits Long".format(doc.name,
                                                                                               pincode_length))
                if country_doc.pincode_regular_expression:
                    pincode_regex = replace_java_chars(country_doc.pincode_regular_expression)
                    if 'or' in pincode_regex:
                        pc_regex = pincode_regex.split("or")
                    else:
                        pc_regex = [pincode_regex]
                    pc_regex_pass = 0
                    for d in pc_regex:
                        p = re.compile(d.strip())
                        if not p.match(doc.pincode):
                            pass
                        else:
                            pc_regex_pass = 1
                    if pc_regex_pass != 1:
                        frappe.throw("Country {}: Pin Code Should be of Format {}".format(doc.country, pincode_regex))
            else:
                frappe.throw("For Country {} no states exists in State Table".format(doc.country))
        else:
            doc.state_rigpl = ""
            if doc.pincode is None:
                frappe.throw("If Pin Code is not Known then Enter NA")
        if doc.state_rigpl:
            doc.state = doc.state_rigpl
            verify_state_country(doc.state_rigpl, doc.country)
    else:
        frappe.throw('Country is Mandatory')


def verify_state_country(state, country):
    state_doc = frappe.get_doc("State", state)
    if state_doc.country != country:
        frappe.throw("State {} belongs to Country {} hence choose correct State or Change Country to {}".
                     format(state, state_doc.country, state_doc.country))


def validate_primary_address(doc, method):
    """Validate that there can only be one primary address for particular customer, supplier"""
    if doc.is_primary_address == 1:
        unset_other(doc, method, "is_primary_address")
    else:
        # This would check if there is any Primary Address if not then would make current as Primary address
        check = check_set(doc, method, "is_primary_address")
        if check == 0:
            doc.is_primary_address = 1


def validate_shipping_address(doc, method):
    """Validate that there can only be one shipping address for particular customer, supplier"""
    if doc.is_shipping_address == 1:
        unset_other(doc, method, "is_shipping_address")
    else:
        # This would check if there is any Shipping Address if not then would make current as Shipping address
        check = check_set(doc, method, "is_shipping_address")
        if check == 0:
            doc.is_shipping_address = 1


def unset_other(doc, method, is_address_type):
    for d in doc.links:
        other_add = frappe.db.sql("""SELECT parent FROM `tabDynamic Link` 
        WHERE link_doctype = '%s' AND link_name = '%s' AND parent != '%s' AND parenttype = '%s'""" %
                                  (d.link_doctype, d.link_name, doc.name, doc.doctype), as_list=1)
    for add in other_add:
        frappe.db.set_value(doc.doctype, add[0], is_address_type, 0)


def check_set(doc, method, is_address_type):
    for d in doc.links:
        other_add = frappe.db.sql("""SELECT parent FROM `tabDynamic Link` 
        WHERE link_doctype = '%s' AND link_name = '%s' AND parent != '%s' AND parenttype = '%s'""" %
                                  (d.link_doctype, d.link_name, doc.name, doc.doctype), as_list=1)
        chk = 0
        for add in other_add:
            chk = chk + flt(frappe.db.get_value(doc.doctype, add[0], is_address_type))
    return chk


def check_id(doc, method):
    # Disallow Special Characters in Customer ID
    new_name = re.sub('[^A-Za-z0-9\\-]+', ' ', doc.name)
    entered_name = doc.name
    return new_name, entered_name


def geocode(doc, method):
    if doc.dont_update_from_google == 1:
        remove_google_updates(doc)
    else:
        if not doc.json_reply:
            geocoding(doc)
            address_dict = render_gmap_json(doc.json_reply)
            if address_dict:
                update_fields_from_gmaps(doc, address_dict)
        else:
            json_dict = ast.literal_eval(doc.json_reply)
            if json_dict.get("status") == "OK":
                address_dict = render_gmap_json(doc.json_reply)
                if address_dict:
                    update_fields_from_gmaps(doc, address_dict)
            else:
                geocoding(doc)


def remove_google_updates(doc):
    doc.json_reply = ""
    doc.latitude = ""
    doc.longitude = ""
    doc.global_google_code = ""
    doc.approximate_location = 0


def update_fields_from_gmaps(doc, address_dict):
    if doc.country == address_dict["country"]:
        if address_dict.get("global_code"):
            doc.global_google_code = address_dict.get("global_code")
        if doc.latitude != address_dict.get("lat"):
            doc.latitude = address_dict.get("lat")
        if doc.longitude != address_dict.get("lng"):
            doc.longitude = address_dict.get("lng")
        if address_dict.get("partial_match") != 1:
            if doc.update_from_google == 1:
                frappe.msgprint("Updating Address Automatically from Google Maps")
                if doc.country != address_dict.get("country"):
                    doc.country = address_dict.get("country")
                if doc.state != address_dict.get("state"):
                    doc.state = address_dict.get("state")
                if doc.city != address_dict.get("city"):
                    # frappe.msgprint(str(address_dict))
                    if address_dict.get("city") == "":
                        doc.city = "NA"
                    else:
                        doc.city = address_dict.get("city")
                if doc.address_line1 != address_dict.get("address_line1"):
                    doc.address_line1 = address_dict.get("address_line1")
                add_line2 = address_dict.get("sublocal1", "") + ", " + address_dict.get("sublocal2", "") \
                            + ", " + address_dict.get("locality", "")
                if doc.address_line2 != add_line2:
                    doc.address_line2 = add_line2
                if doc.pincode != address_dict.get("postal_code"):
                    doc.pincode = address_dict.get("postal_code")
            else:
                frappe.msgprint("You can update Address: {} directly from Google. For this Click on Check "
                                "Box to Update Directly from Google.".format(doc.name))
        else:
            doc.approximate_location = 1
    else:
        doc.dont_update_from_google = 1
        remove_google_updates(doc)


def validate_gstin_from_portal(doc):
    auto_days = flt(frappe.get_value("Rohit Settings", "Rohit Settings", "auto_validate_gstin_after"))
    if doc.gst_validation_date:
        days_since_validation = (date.today() - getdate(doc.gst_validation_date)).days
    else:
        days_since_validation = 999
    if doc.validated_gstin != doc.gstin or days_since_validation >= auto_days:
        # Validate GSTIN status after 30 days if done manually changes
        gstin_json = search_gstin(doc.gstin)
        doc.gstin_json_reply = str(gstin_json)
        doc.validated_gstin = gstin_json.get("gstin")
        doc.gst_status = gstin_json.get("sts")
        doc.gst_validation_date = date.today()
    if doc.gst_status in ('Inactive', 'Cancelled'):
        doc.disabled = 1
    elif doc.gst_status == 'Suspended':
        # Disable the address for Supplier or unlinked address
        dl_list = frappe.db.sql("""SELECT name, link_doctype FROM `tabDynamic Link` WHERE parenttype = 'Address'
        AND parent = '%s'""" % doc.name, as_dict=1)
        if dl_list:
            for dt in dl_list:
                if dt.link_doctype == 'Supplier':
                    doc.disabled = 1
        else:
            doc.disabled = 1
    update_address_title_from_gstin_json(doc)


def update_address_title_from_gstin_json(doc):
    if doc.validated_gstin:
        if doc.validated_gstin == doc.gstin:
            gst_json = ast.literal_eval(doc.gstin_json_reply)
            if gst_json.get("status_cd", 1) == 1:
                # Now Check the Legal Name lgnm and Also another field is Trade Name (tradeNam)
                lgl_name = gst_json.get("lgnm")
                trd_name = gst_json.get("tradeNam")
                lgl_ratio = sm(lambda x: x in (" ", ".", ",", "(", ")"), (doc.address_title).lower(),
                               lgl_name.lower()).ratio()
                trd_ratio = sm(lambda x: x in (" ", ".", ",", "(", ")"), (doc.address_title).lower(),
                               trd_name.lower()).ratio()
                if lgl_ratio > 0.6:
                    # Update Address Title from Legal Name
                    doc.address_title = lgl_name
                    frappe.msgprint("Updated Address Title from Legal Name on GST Website for {}".format(doc.name))
                elif trd_ratio > 0.6:
                    # Update Address Title from Legal Name
                    doc.address_title = trd_name
                    frappe.msgprint("Updated Address Title from Trade Name on GST Website for {}".format(doc.name))
