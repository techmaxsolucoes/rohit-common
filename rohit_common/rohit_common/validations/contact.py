#  Copyright (c) 2022. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import frappe
from ...utils.rohit_common_utils import check_or_rename_doc
from ...utils.contact_utils import validate_contact_master, all_contact_email_validations, \
    all_contact_phone_validations, all_contact_text_validations


def autoname(doc, method):
    """
    Automatically renames the document
    """
    backend = 0
    if doc.flags.ignore_mandatory == 1:
        backend = 1
    check_or_rename_doc(doc, backend)


def validate(doc, method):
    """
    Validate the Email and Would move Multiple Emails in Single Row in Multiple Rows
    """
    if doc.flags.ignore_mandatory == 1:
        backend = 1
    else:
        backend = 0
    validate_contact_master(doc, backend=backend)
    all_contact_text_validations(doc, backend=backend)
    all_contact_phone_validations(doc, backend=backend)
    all_contact_email_validations(doc, backend=backend)
    check_or_rename_doc(doc, backend)
