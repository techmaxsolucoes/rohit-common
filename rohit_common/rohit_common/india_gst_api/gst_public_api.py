# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Group Private Limited and contributors
# For license information, please see license.txt
import frappe
import json
from .common import get_gsp_details
# from erpnext.accounts.utils import get_fiscal_year
import requests


def search_gstin(gstin=None):
    gsp_link, asp_id, asp_pass, caller_gstin = get_gsp_details(api_type="common", action='TP', api='search')
    if not gstin:
        gstin = caller_gstin
    full_url = gsp_link + '&Gstin=' + caller_gstin + '&SearchGstin=' + gstin
    response = requests.get(full_url)
    json_response = response.json()
    return json_response


def track_return(gstin, fiscal_year):
    # (fiscal_year, start_date, end_date) = get_fiscal_year(for_date)
    fy_format = fiscal_year[:5] + fiscal_year[7:]
    gsp_link, asp_id, asp_pass, caller_gstin = get_gsp_details(api_type="common", action='RETTRACK', api="returns")
    full_url = gsp_link + '&Gstin=' + gstin + '&FY=' + fy_format
    response = requests.get(full_url)
    # frappe.throw(str(response.text))
    json_response = response.json()
    # frappe.throw(str(json_response))
    return json_response
