# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Group Private Limited and contributors
# For license information, please see license.txt
import frappe
import requests


def get_version(api=None):
    if api == 'search':
        return 'v1.1'
    elif api in ['returns', 'asp']:
        return 'v1.0'
    elif api == 'eway':
        return 'v1.03'
    else:
        return ''


def get_api_url(api, action, api_type=None):
    version = get_version(api)
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
    gsp_link = rset.api_link
    asp_id = rset.tax_pro_asp_id
    asp_pass = rset.tax_pro_password
    if not gstin:
        if api_type == 'common':
            gstin = rset.gstin
        else:
            if rset.sandbox_mode == 1:
                gstin = '05AAACG1539P1ZH'
            else:
                gstin = rset.gstin

    gsp_sandbox_link = rset.sandbox_api_link
    api_url = '/' + api
    if api_type == "common":
        api_url = get_api_url(api=api, action=action, api_type=api_type)
    else:
        if rset.sandbox_mode == 1:
            gsp_link = gsp_sandbox_link
    if api_type == 'common':
        gsp_link = gsp_link + api_url+ 'aspid=' + asp_id + '&password=' + asp_pass + '&Action=' + action

    return gsp_link, asp_id, asp_pass, gstin
