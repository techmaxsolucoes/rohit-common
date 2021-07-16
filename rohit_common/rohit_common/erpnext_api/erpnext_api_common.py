#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
# -*- coding: utf-8 -*-
import frappe
import requests
timeout = 5

def get_login_details():
    base_link = ""
    auth_header = ""
    rset = frappe.get_doc("Rohit Settings", "Rohit Settings")
    if rset.api_key:
        auth_header = {"Authorization": "token " + rset.api_key + ":" + rset.api_secret}
        base_link = rset.erpnext_app_base_link
    else:
        print(f"No Settings for ERP API Exiting")
    return base_link, auth_header


def get_dt(dt, dt_name=None, fields_list=None, filters=None):
    # filters is list of list
    base_url, auth_header = get_login_details()
    if base_url != "":
        fd_lnk = ""
        dtn_lnk = ""
        f_lnk = ""
        if filters:
            if not fields_list:
                f_lnk += "?filters=["
            else:
                f_lnk += "&filters=["
            for fd in filters:
                f_lnk += "["
                for fdn in fd:
                    if isinstance(fdn, int):
                        f_lnk += str(fdn) + ", "
                    else:
                        f_lnk += '"' + str(fdn) + '", '
                f_lnk = f_lnk[:-2] + "], "
            f_lnk = f_lnk[:-2] + "]"
        if dt_name:
            dtn_lnk += "/" + dt_name
        if fields_list:
            fd_lnk = "?fields=["
            for fd in fields_list:
                if isinstance(fd, int):
                    fd_lnk += fd + ", "
                else:
                    fd_lnk += '"' + fd + '", '
            fd_lnk = fd_lnk[:-2] + "]"
        link = base_url + "/api/resource/" + dt + dtn_lnk + fd_lnk + f_lnk
        r = requests.get(url=link, headers=auth_header, timeout=timeout)
        return r.json()
    else:
        return None
