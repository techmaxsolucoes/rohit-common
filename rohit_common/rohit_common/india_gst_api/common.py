#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-
import frappe
from datetime import datetime
from frappe.utils import flt


def get_api_version(api):
    api_version_list = [
        {"api": "search", "version": "v1.1", "action": "TP"}, {"api": "returns", "version": "v1.0", "action": "TP"},
        {"api": "asp", "version": "v1.0", "action": "TP"}, {"api": "eway", "version": "v1.03", "action": "TP"},
        {"api": "search", "version": "v1.1", "action": "TP"},
        {"api": "otp", "version": "v1.0", "action": "authenticate"},
        {"api": "gstr2a", "version": "v2.0", "action": "returns/gstr2a"}
    ]
    for d in api_version_list:
        if d["api"] == api:
            return d["version"], d["action"]


def get_api_url(api, api_type=None):
    version, act_type = get_api_version(api)
    rset = frappe.get_single('Rohit Settings')
    if api_type == "common":
        api_url = '/' + api_type + 'api/' + version + '/' + api + '/?'
    elif api == 'eway':
        if rset.sandbox_mode == 1:
            api_url = '/' + api + 'billapi/dec/' + version + '/'
        else:
            api_url = '/' + version + '/dec/'
    elif api == 'asp':
        api_url = '/' + api + 'api/' + version + '/'
    return api_url


def get_gsp_details(api, action, gstin=None, api_type=None):
    rset = frappe.get_single('Rohit Settings')
    sandbox = rset.sandbox_mode
    gsp_link = rset.api_link
    asp_id = rset.tax_pro_asp_id
    asp_pass = rset.tax_pro_password
    if not gstin:
        if api_type == 'common':
            gstin = rset.gstin
        else:
            if sandbox == 1:
                gstin = '05AAACG1539P1ZH'
            else:
                gstin = rset.gstin

    gsp_sandbox_link = rset.sandbox_api_link
    api_url = '/' + api
    if api_type == "common":
        api_url = get_api_url(api=api, api_type=api_type)
    else:
        if rset.sandbox_mode == 1:
            gsp_link = gsp_sandbox_link
    if api_type == 'common':
        gsp_link = gsp_link + api_url + 'aspid=' + asp_id + '&password=' + asp_pass + '&Action=' + action

    return gsp_link, asp_id, asp_pass, gstin, sandbox


def gst_return_period_validation(return_period):
    month = flt(return_period[:2])
    year = flt(return_period[2:])
    now = datetime.now()
    message = f"Return Period Format is MMYYYY. {return_period} does not conform to that format"
    if len(return_period) != 6:
        frappe.throw(message)
    if month < 1 or month > 12:
        frappe.throw(message)
    if year < 2017 or year > now.year:
        frappe.throw("Year Cannot be in Future or Before 2017")
    elif year == 2017:
        if month < 7:
            frappe.throw("Return Period Cannot be Before July-2017")
    elif year == now.year:
        if month >= now.month:
            frappe.throw("Return Period Can only be for Past Months")


def validate_gstin(gstin):
    if len(gstin) != 15:
        frappe.throw(f"GST Number: {gstin} Should be of 15 Characters")
