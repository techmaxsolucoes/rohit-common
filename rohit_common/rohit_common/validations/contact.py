# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from ...utils.contact_utils import validate_contact_master, all_contact_email_validations, \
    all_contact_phone_validations, all_contact_text_validations



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
