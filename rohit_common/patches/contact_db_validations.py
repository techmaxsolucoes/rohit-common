#  Copyright (c) 2022. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

import frappe
import time
from frappe.utils import flt
from ..utils.rohit_common_utils import check_or_rename_doc
from ..utils.contact_utils import get_contact_country


def master_renaming():
    """
    Gets a list of all masters and checks it as per the rules and renames them
    """
    st_time = time.time()
    doc_list = ["Account", "Address", "Contact", "Customer", "Supplier"]
    for dtyp in doc_list:
        renamed = 0
        dt_dict = frappe.db.sql(f"""SELECT name FROM `tab{dtyp}` ORDER BY creation DESC""", as_dict=1)
        if dt_dict:
            print(f"Total {dtyp} to be Checked = {len(dt_dict)}")
            for dtn in dt_dict:
                dtd = frappe.get_doc(dtyp, dtn.name)
                renaming_done = flt(check_or_rename_doc(dtd, backend=1))
                renamed += renaming_done
                if renamed > 0 and renamed % 10 == 0 and renaming_done > 0:
                    print(f"Committing Changes after {renamed} Documents")
                    frappe.db.commit()
                    print(f"Total Time Elapsed Till Now {int(time.time()-st_time)} seconds")
        print(f"Total {dtyp} Renamed = {renamed} and Total Time Taken = \
            {int(time.time() - st_time)} seconds")



def contact_phone_nos_validation():
    """
    This patch would look for contacts where phone numbers are not validated and would
    try to validate the same
    """
    st_time = time.time()
    cont_phones = frappe.db.sql("""SELECT ph.name, ph.phone, ph.is_primary_phone,
        ph.is_primary_mobile_no, ph.is_possible, ph.is_valid, ph.is_mobile, ph.country, ph.parent,
        ph.parenttype FROM `tabContact Phone` ph WHERE ph.country IS NULL OR ph.is_valid = 0
        OR ph.is_possible = 0 ORDER BY ph.parenttype, ph.parent, ph.idx""", as_dict=1)
    print(f"Total number of Phones To be Validated = {len(cont_phones)} ")
    input("Press Any key to Continue...")
    for phone in cont_phones:
        if not phone.country:
            if phone.parenttype == "Contact":
                con_doc = frappe.get_doc("Contact", phone.parent)
                country = get_contact_country(con_doc)
                if country:
                    print(f"Updating Row# {phone.idx} for {phone.parenttype}:{phone.parent}")
                    frappe.db.set_value("Contact Phone", phone.name, phone.country)
                else:
                    print(f"For {phone.parenttype}: {phone.parent} at Row# {phone.idx} cannot \
                        determine the Country")
                    input("Press Any key to Continue...")
            else:
                print(f"{phone} has a different type of Parent New Code Needed")
                break
