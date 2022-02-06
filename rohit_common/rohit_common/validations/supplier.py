# Copyright (c) 2022 Rohit Industries Group Private Limited and Contributors.
# For license information, please see license.txt
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from ...utils.rohit_common_utils import check_or_rename_doc


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
    Validate the Names as per the rules
    """
    if doc.flags.ignore_mandatory == 1:
        backend = 1
    else:
        backend = 0
    check_or_rename_doc(doc, backend)
