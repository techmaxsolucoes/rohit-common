# Copyright (c) 2022, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import re
import frappe
from frappe.utils import flt
from ..rohit_common.validations.google_maps import get_geocoded_address_dict
from .rohit_common_utils import replace_java_chars, santize_listed_txt_fields


def all_address_text_validations(adr_doc):
    """
    Sanitizes all the text fields as pe the field dict
    """
    field_dict = [frappe._dict({})]

    field_dict = [
        {"field_name": "address_title", "case":"upper"},
        {"field_name": "address_line1", "case":"title"},
        {"field_name": "address_line2", "case":"title"},
        {"field_name": "city", "case":"title"}, {"field_name": "state", "case":"title"},
        {"field_name": "county", "case":"title"}, {"field_name": "pincode", "case":"upper"},
        {"field_name": "sea_port", "case":"upper"}, {"field_name": "airport", "case":"upper"},
        {"field_name": "phone", "case":""}, {"field_name": "fax", "case":""},
        {"field_name": "gstin", "case":"upper"}
    ]
    santize_listed_txt_fields(adr_doc, field_dict)


def guess_address_comps_from_geocoding(add_doc, ):
    """
    Tries to guess the Missing Address fields from GeoCoded Data
    """
    adr_dict = get_geocoded_address_dict(add_doc)
    if add_doc.country == adr_dict.country:
        if add_doc.state == adr_dict.state:
            pass


def pin_length_status(add_doc, backend=True):
    """
    Checks if the length of the pincode is as per the Country's format
    """
    add_doc.pincode = re.sub('[^A-Za-z0-9]+', '', str(add_doc.pincode))
    plen = frappe.get_value("Country", add_doc.country, "pincode_length")
    if plen:
        plen_form = replace_java_chars(plen)
        if 'or' in plen_form:
            pc_length = plen_form.split("or")
        else:
            pc_length = [plen_form]
        pin_len_pass = 0
        for form in pc_length:
            if add_doc.pincode:
                add_doc.pincode = add_doc.pincode.strip()
                if len(add_doc.pincode) == flt(form):
                    pin_len_pass = 1
        if pin_len_pass != 1:
            message = (f"For Address {add_doc.name}: with Country: {add_doc.country} and "
                        f"State: {add_doc.state_rigpl} and Pincode: {add_doc.pincode} "
                        f"should be {plen_form} Digits Long")
            if backend != 1:
                frappe.throw(message)
            else:
                print(message)
                return 0
        else:
            return 1
    else:
        return 1


def pin_regex_status(add_doc, backend=True):
    """
    Checks the Pincode for regex for a Country's Matching Style and returns boolean after matching
    """
    pc_regex_pass = 0
    pc_regex = frappe.get_value("Country", add_doc.country, "pincode_regular_expression")
    if pc_regex:
        if add_doc.pincode:
            pc_regex_form = replace_java_chars(pc_regex)
            if 'or' in pc_regex_form:
                pc_regex_py = pc_regex_form.split("or")
            else:
                pc_regex_py = [pc_regex_form]
            for alp in pc_regex_py:
                comp_alp = re.compile(alp.strip())
                if not comp_alp.match(add_doc.pincode):
                    pass
                else:
                    pc_regex_pass = 1
            if pc_regex_pass != 1:
                message = (f"Country {add_doc.country}: State: {add_doc.state_rigpl} Pin Code: "
                    f"{add_doc.pincode} Should be of Format Regular Expression: {pc_regex_py}")
                if backend != 1:
                    frappe.throw(message)
                else:
                    print(message)
    else:
        pc_regex_pass = 1
    return pc_regex_pass


def state_as_per_country(add_doc, backend=True):
    """
    Checks if the address doc has the correct state. Basically it checks with the country master
    if the Country has known states then RIGPL_STATE field should be within state table and
    also should be with matching country
    Returns 0 when we cannot try address correction, 1 = No State correction needed
    """
    known_states = frappe.get_value("Country", add_doc.country, "known_states")
    if known_states == 1:
        if not add_doc.state_rigpl:
            return 0
        else:
            state_tbl = frappe.db.sql(f"""SELECT name FROM `tabState` WHERE name =
                '{add_doc.state_rigpl}' AND country = '{add_doc.country}'""", as_dict=1)
            if state_tbl:
                if add_doc.state != add_doc.state_rigpl:
                    add_doc.state = add_doc.state_rigpl
                return 1
            else:
                message = (f"{add_doc.name} for Country: {add_doc.country} the State: "
                    f"{add_doc.state_rigpl} is Not In State Table")
                if backend == 1:
                    print(message)
                    return 0
                else:
                    frappe.throw(message)
    else:
        if add_doc.state_rigpl:
            add_doc.state_rigpl = ""
        return 1



def get_country_for_master(link_type, link_name):
    """
    Returns country for addresses of a Link Type and Link Name
    If there are multiple addresses with different country then it would return None
    If the country is same in Multiple addresses then only it would return a country
    """
    add_dict = get_address_for_master(link_type, link_name)
    if add_dict:
        base_country = None
        for adr in add_dict:
            if base_country:
                if adr.country != base_country:
                    return None
                else:
                    base_country = adr.country
            else:
                base_country = adr.country
    return base_country



def get_address_for_master(link_type, link_name):
    """
    Returns country for Address Master Linkage
    """
    add_dict = frappe.db.sql(f"""SELECT ad.name, ad.country
        FROM `tabAddress` ad, `tabDynamic Link` dl WHERE dl.link_doctype = '{link_type}'
        AND dl.link_name = '{link_name}' AND dl.parent = ad.name
        AND dl.parenttype = 'Address'""", as_dict=1)
    return add_dict
