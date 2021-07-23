#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-
import frappe
import datetime
import requests
from frappe.utils import flt, getdate
from .common import get_gsp_details, get_api_version
timeout = 7


def get_gstr1(gstin, ret_period, action):
    api = "gstr1"
    auth_token = get_auth_token(gstin)
    url = get_gst_url(api, action, gstin) + "&authtoken=" + auth_token + "&ret_period=" + ret_period
    resp = get_gst_response(url=url, type_of_req="get")
    # frappe.throw(str(resp))
    if flt(resp.get("status_cd")) == 1:
        return resp
    elif resp.get(action.lower(), None) is not None:
        return resp
    elif flt(resp.get("status_cd")) == 0:
        return []
    else:
        frappe.throw(f"Some Error in Response with Error Message = {resp} URL Used= {url}")


def get_gstr2a(gstin, ret_period, action):
    api = "gstr2a"
    auth_token = get_auth_token(gstin)
    url = get_gst_url(api, action, gstin) + "&authtoken=" + auth_token + "&ret_period=" + ret_period
    resp = get_gst_response(url=url, type_of_req="get")
    if flt(resp.get("status_cd")) == 1:
        return resp
    elif resp.get(action.lower(), None) is not None:
        return resp
    elif flt(resp.get("status_cd")) == 0:
        return []
    else:
        frappe.throw(f"Some Error in Response with Error Message = {resp} URL Used= {url}")


def get_gstr2b(gstin, ret_period, action, file_num=None):
    if file_num:
        file_num_link = "&file_num" + file_num
    else:
        file_num_link = ""
    api = "gstr2b"
    auth_token = get_auth_token(gstin)
    url = get_gst_url(api, action, gstin) + "&authtoken=" + auth_token + "&rtnprd=" + ret_period + "&ret_period=" + \
          ret_period + file_num_link
    # frappe.throw(url)
    resp = get_gst_response(url=url, type_of_req="get")
    # frappe.msgprint(f"{resp}")
    if resp.get("chksum"):
        return resp
    else:
        frappe.throw(f"Some Error in Response with Error Message = {resp} URL Used= {url}")


def get_gst_response(url, type_of_req):
    if type_of_req == "post":
        return requests.post(url=url, timeout=timeout).json()
    elif type_of_req == "get":
        return requests.get(url=url, timeout=timeout).json()
    else:
        frappe.throw(f"Type of Request {type_of_req} is Not Defined")


@frappe.whitelist()
def get_gst_otp(gstin):
    api = "otp"
    action = "OTPREQUEST"
    otp_url = get_gst_url(api=api, action=action, gstin=gstin)
    res = requests.get(otp_url, timeout=timeout).json()
    if flt(res.get("status_cd")) == 1:
        frappe.msgprint("OTP Sent Successfully, Please enter the OTP sent to RMN")
    else:
        frappe.msgprint(f"OTP Generation Failed. Please try again later. Error Message is {res} and OTP URL {otp_url}")


@frappe.whitelist()
def authenticate_gst_otp(gstin, otp, row_id):
    # gst_reg = frappe.get_doc("GST Registration Details", row_id)
    api = "otp"
    action = "AUTHTOKEN"
    auth_url = get_gst_url(api=api, action=action, gstin=gstin) + "&OTP=" + otp
    #print(auth_url)
    # auth_url = "http://gstsandbox.charteredinfo.com/taxpayerapi/dec/v1.0/authenticate?
    # action=AUTHTOKEN&aspid=1641491220&password=NRjnagyWb36@b5kC&gstin=27GSPMH0041G1ZZ
    # &username=Chartered.MH.1&OTP=575757"
    # print(auth_url)
    auth_resp = requests.get(url=auth_url, timeout=timeout)
    print(auth_resp)
    auth_resp = auth_resp.json()
    print(auth_resp)
    if flt(auth_resp.get("status_cd")) == 1:
        frappe.db.set_value("GST Registration Details", row_id, "last_otp_sent",
                datetime.datetime.now())
        update_auth_token(row_name=row_id, auth_token=auth_resp.get("auth_token"))
        frappe.msgprint(f"Updated the Auth Token. Now API access to {gstin} is Active")
    else:
        update_auth_token(row_name=row_id, auth_token="", failed=1)
        frappe.throw(f"OTP Validation Failed and Error Message = {auth_resp} and Link = {auth_url}")


def check_for_refresh_token(row):
    now_time = datetime.datetime.now()
    token_time = flt(row.update_token_every_mins)
    if row.authorization_token and row.api_access_authorized == 1:
        token_update_time = row.validity_of_token - datetime.timedelta(minutes=360) + datetime.timedelta(minutes=token_time)
        if token_update_time < now_time and row.validity_of_token > now_time:
            new_auth_token, error_code = refresh_auth_token(row.gst_registration_number, row.authorization_token)
            if new_auth_token != "":
                print(f"Auto Updated Auth Token for {row.gst_registration_number}")
                update_auth_token(row_name=row.name, auth_token=new_auth_token)
            else:
                print(f"Auto Auth Token Update Failed for {row.gst_registration_number}")
                update_auth_token(row_name=row.name, auth_token="", failed=1, error_code=error_code)
        elif token_update_time > now_time and row.validity_of_token > now_time:
            print(f"No Need to Update the Auth Token for {row.gst_registration_number} as Token to be Updated After {token_update_time}")
        else:
            print(f"Auth Token is Expired and hence Need to Generate OTP Again for {row.gst_registration_number}")
            update_auth_token(row_name=row.name, auth_token="", failed=1, error_code='AUTH4037')
    elif row.api_access_authorized != 1:
        print(f"API Authorization is Unchecked for {row.gst_registration_number}")
    else:
        print(f"No API Authorization Token for {row.gst_registration_number}")


def refresh_auth_token(gstin, auth_token):
    error_code = ""
    api = "otp"
    action = "REFRESHTOKEN"
    ref_url = get_gst_url(api=api, action=action, gstin=gstin) + "&AuthToken=" + auth_token
    ref_resp = requests.get(url=ref_url, timeout=timeout).json()
    if flt(ref_resp.get("status_cd")) == 1:
        return ref_resp.get("auth_token"), error_code
    else:
        error = ref_resp.get('error')
        print(f"Some Error in Refreshing the Auth Token with Error = {ref_resp.get('error')} and URL "
                        f"being used = {ref_url} and full response is {ref_resp}")
        error_code = error.get("error_cd")
        return "", error_code


def get_auth_token(gstin):
    found = 0
    r_set = frappe.get_doc("Rohit GST Settings", "Rohit GST Settings")
    now_time = datetime.datetime.now()
    for d in r_set.gst_registration_details:
        if d.gst_registration_number == gstin:
            token_update_min = flt(d.update_token_every_mins)  # Updates token after this many mins
            token_update_time = d.validity_of_token - datetime.timedelta(minutes=360) + datetime.timedelta(minutes=token_update_min)
            found = 1
            if d.authorization_token and d.api_access_authorized == 1:
                if token_update_time > now_time and d.validity_of_token > now_time:
                    return d.authorization_token
                elif token_update_time < now_time < d.validity_of_token:
                    new_auth_token, error_code = refresh_auth_token(gstin=gstin, auth_token=d.authorization_token)
                    if new_auth_token != "":
                        update_auth_token(row_name=d.name, auth_token=new_auth_token, error_code=error_code)
                        return new_auth_token
                    else:
                        update_auth_token(row_name=d.name, auth_token="", failed=1, error_code=error_code)
                        frappe.throw(f"New Auth Token for {gstin} is Empty you might need to Generate OTP Again")
                else:
                    update_auth_token(row_name=d.name, auth_token="", failed=1, error_code="AUTH4037")
                    frappe.throw(f"Auth Token for {gstin} is Expired you might need to Generate OTP Again")
            else:
                frappe.throw(f"Authorization Needed for {gstin}. Resend OTP and Get Authorization")
    if found == 0:
        frappe.throw(f"{gstin} is Not Setup in Rohit GST Settings for API Access")


def update_auth_token(row_name, auth_token, failed=0, error_code=None):
    if not error_code:
        error_code = ""
    ecl = ["AUTH4037", "RET11402", "SWEB9033", "AUTH4033", "GSP102"]
    if failed == 1:
        # Only Update API Access to zero on certain errors and not all errors
        frappe.db.set_value("GST Registration Details", row_name, "otp", "")
        if error_code != "" and error_code in ecl:
            print(f"Removing API Access")
            frappe.db.set_value("GST Registration Details", row_name, "api_access_authorized", 0)
        else:
            print(f"Error Code: {str(error_code)} Not in List")
        frappe.db.commit()
    else:
        auth_access = flt(frappe.db.get_value("GST Registration Details", row_name, "api_access_authorized"))
        exist_token_times = flt(frappe.db.get_value("GST Registration Details", row_name, "no_of_times_token_updated"))
        if auth_access == 1:
            frappe.db.set_value("GST Registration Details", row_name, "no_of_times_token_updated", exist_token_times + 1)
        else:
            frappe.db.set_value("GST Registration Details", row_name, "no_of_times_token_updated", 0)
        frappe.db.set_value("GST Registration Details", row_name, "api_access_authorized", 1)
        frappe.db.set_value("GST Registration Details", row_name, "authorization_token", auth_token)
        frappe.db.set_value("GST Registration Details", row_name, "otp", "")
        frappe.db.set_value("GST Registration Details", row_name, "validity_of_token",
                            datetime.datetime.now() + datetime.timedelta(minutes=360))

def logout_gst():
    url = "http://gstsandbox.charteredinfo.com/taxpayerapi/dec/v1.0/authenticate?action=LOGOUT&aspid=1641491220&password=NRjnagyWb36@b5kC&gstin=27GSPMH0041G1ZZ&username=Chartered.MH.1&authtoken=295898a7acb348f29f67afbada72e4b4"
    resp = requests.get(url)
    print(resp)
    resp = resp.json()
    print(resp)


def get_gst_url(api, action, gstin):
    gsp_link, asp_id, asp_pass, gstin_other, sandbox = get_gsp_details(api=api, action=action)
    username = get_gst_username(gstin=gstin)
    version, act_type = get_api_version(api)
    gst_url = gsp_link + "/taxpayerapi/dec/" + version + "/" + act_type + "?action=" + action + "&aspid=" + asp_id + \
              "&password=" + asp_pass + "&gstin=" + gstin + "&username=" + username
    return gst_url


def get_gst_username(gstin):
    found = 0
    r_set = frappe.get_doc("Rohit GST Settings", "Rohit GST Settings")
    for d in r_set.gst_registration_details:
        if d.gst_registration_number == gstin:
            found = 1
            return d.gst_username
    if found == 0:
        frappe.throw(f"No GSTIN username found for {gstin}")


def get_invoice_type(itype):
    if itype == "R":
        return "R-Regular B2B Invoices"
    elif itype == "DE":
        return "DE-Deemed Exports"
    elif itype == "SEWP":
        return "SEWP-SEZ Exports with payment"
    elif itype == "SEWOP":
        return "SEWOP-SEZ exports without payment"


def get_type_of_amend(amend_type):
    if amend_type == "R":
        return "R-Receiver GSTIN Amended"
    elif amend_type == "N":
        return "N-Invoice Number Amended"
    elif amend_type == "D":
        return "D-Details Amended"
