# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
import re
import ast

from .google_maps import geocoding, render_gmap_json, get_google_maps_api_key
from frappe.utils import flt


def validate(doc, method):
    validate_primary_address(doc, method)
    validate_shipping_address(doc, method)
    doc.pincode = re.sub('[^A-Za-z0-9]+', '', str(doc.pincode))
    valid_chars_gstin = "0123456789ABCDEFGIHJKLMNOPQRSTUVYWXZ"

    if doc.country:
        if doc.country == 'India':
            if doc.state_rigpl is None:
                frappe.throw('State RIGPL for Country India is Mandatory')
            else:
                doc.state = doc.state_rigpl
                doc.gst_state = doc.state_rigpl
            if len(doc.pincode) != 6:
                frappe.throw('India Pincode should always be 6 Digits')
            else:
                p = re.compile("[0-9]{6}")
                if not p.match(doc.pincode):
                    frappe.throw(_("Invalid Pincode only digits in Pincode for India allowed"))
        elif doc.country == 'United States':
            doc.gstin = 'NA'
            doc.gst_state = ""
            doc.gst_state_number = ""

            if doc.state_rigpl is None:
                frappe.throw('State RIGPL for Country US is Mandatory')
            else:
                doc.state = doc.state_rigpl
                doc.gst_state = ""
            if len(doc.pincode) == 5:
                p = re.compile("[0-9]{5}")
                if not p.match(doc.pincode):
                    frappe.throw(_("Invalid Pincode only digits in Pincode for US allowed"))
            elif len(doc.pincode) == 9:
                p = re.compile("[0-9]{9}")
                if not p.match(doc.pincode):
                    frappe.throw(_("Invalid Pincode only digits in Pincode for US allowed"))
            else:
                frappe.throw('US Pincode should always be 5 or 9 Digits')
        else:
            doc.gstin = 'NA'
            doc.gst_state = ""
            doc.gst_state_number = ""
            doc.state_rigpl = ""
            if doc.pincode is None:
                frappe.throw("If Pincode is not Known then Enter NA")
        if not doc.state or doc.state == '':
            frappe.throw("State field is Mandatory")
    else:
        frappe.throw('Country is Mandatory')

    if doc.state_rigpl:
        doc.state = doc.state_rigpl
        verify_state_country(doc.state_rigpl, doc.country)

    if doc.gstin:
        if doc.gstin != "NA":
            if len(doc.gstin) != 15:
                frappe.msgprint("GSTIN should be exactly as 15 digits or NA", raise_exception=1)
            else:
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
            if doc.gstin != "NA":
                doc.pan = doc.gstin[2:12]
            else:
                doc.pan = ""
    else:
        if doc.country == 'India':
            frappe.throw('GSTIN Mandatory for Indian Addresses or Enter NA for NO GSTIN')
    geocode(doc, method)


# Todo: Add the GST check digit checksum for the last digit so that all GST numbers are
# checked and entered properly.

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
        doc.json_reply = ""
        doc.latitude = ""
        doc.longitude = ""
        doc.global_google_code = ""
        doc.approximate_location = 0
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


def update_fields_from_gmaps(doc, address_dict):
    # frappe.msgprint(str(address_dict))
    if address_dict.get("global_code"):
        doc.global_google_code = address_dict.get("global_code")
        # global_code = address_dict.get("global_code")
        '''
        key = get_google_maps_api_key()
        iframe_code = '<iframe width="600" height="450" frameborder="0" style="border:0" ' \
                      'src="https://www.google.com/maps/embed/v1/place?q=' + global_code + '&key=' + \
                      key + '" allowfullscreen></iframe> '
        doc.google_maps_view = iframe_code
        '''
    if doc.latitude != address_dict.get("lat"):
        doc.latitude = address_dict.get("lat")
    if doc.longitude != address_dict.get("lng"):
        doc.longitude = address_dict.get("lng")
    if address_dict.get("partial_match") != 1:
        # frappe.msgprint(str(address_dict))
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
        doc.approximate_location = 1
