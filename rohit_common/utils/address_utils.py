# Copyright (c) 2022, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


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
