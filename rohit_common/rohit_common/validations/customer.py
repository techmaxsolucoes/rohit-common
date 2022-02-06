#  Copyright (c) 2022. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

import frappe
from ...utils.rohit_common_utils import check_or_rename_doc


def autoname(doc, method):
    backend = 0
    if doc.flags.ignore_mandatory == 1:
        backend = 1
    check_or_rename_doc(doc, backend)


def validate(doc, method):
    """
    Some Validations for Naming Customer
    """
    if doc.flags.ignore_mandatory == True:
        backend = 1
    else:
        backend = 0
    check_or_rename_doc(doc, backend)

