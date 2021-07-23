#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt
import frappe
import time
from ..india_gst_api.gst_api import check_for_refresh_token


def execute():
    st_time = time.time()
    r_set = frappe.get_doc("Rohit GST Settings", "Rohit Settings")
    for d in r_set.gst_registration_details:
        check_for_refresh_token(row=d)
    r_set.reload()
    print(f"Total Time Taken = {int(time.time() - st_time)} seconds")
