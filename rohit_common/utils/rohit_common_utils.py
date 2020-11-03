# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def check_sales_taxes_integrity(document):
    template = frappe.get_doc("Sales Taxes and Charges Template", document.taxes_and_charges)
    if len(template.taxes) != len(document.taxes):
        frappe.throw("Tax Template {} Data does not match with Document# {}'s Tax {}".
                     format(template.name,document.name, document.taxes_and_charges))
    if document.taxes:
        for tax in document.taxes:
            for temp in template.taxes:
                if tax.idx == temp.idx:
                    if tax.charge_type != temp.charge_type or tax.row_id != temp.row_id or tax.account_head != \
                            temp.account_head or tax.included_in_print_rate != temp.included_in_print_rate or tax.rate !=\
                            temp.rate:
                        frappe.throw(("Selected Tax {0}'s table does not match with tax table of Sales Order# {1}. Check "
                                      "Row # {2} or reload Taxes").format(document.taxes_and_charges, document.name,
                                                                          tax.idx))
    else:
        frappe.throw("Empty Tax Table is not Allowed for Sales Invoice {0}".format(document.name))


def check_dynamic_link(parenttype, parent, link_doctype, link_name):
    link_type = frappe.db.sql("""SELECT name FROM `tabDynamic Link` 
        WHERE docstatus = 0 AND parenttype = '%s' AND parent = '%s'
        AND link_doctype = '%s' AND link_name = '%s'""" % (parenttype, parent, link_doctype, link_name), as_list=1)
    if not link_type:
        frappe.throw("{} {} does not belong to {} {}".format(parenttype, parent, link_doctype, link_name))


def replace_java_chars(string):
    replace_dict = {
        "false": "False",
        "true": "True",
        "&&": " and ",
        "||": " or ",
        "&gt;": ">",
        "&lt;": "<"
    }
    for k, v in replace_dict.items():
        string = string.replace(k, v)
    return string


def fn_check_digit(id_without_check):
    # This code generates the checkdigit for a given string
    # allowable characters within identifier
    valid_chars = "0123456789ABCDEFGHJKLMNPQRSTUVYWXZ"

    # remove leading or trailing whitespace, convert to uppercase
    id_without_checkdigit = id_without_check.strip().upper()

    # this will be a running total
    sum = 0;

    # loop through digits from right to left
    for n, char in enumerate(reversed(id_without_checkdigit)):

        if not valid_chars.count(char):
            frappe.throw('Invalid Character has been used for Item Code check Attributes')

        # our "digit" is calculated using ASCII value - 48
        digit = ord(char) - 48

        # weight will be the current digit's contribution to
        # the running total
        weight = None
        if (n % 2 == 0):

            # for alternating digits starting with the rightmost, we
            # use our formula this is the same as multiplying x 2 &
            # adding digits together for values 0 to 9.  Using the
            # following formula allows us to gracefully calculate a
            # weight for non-numeric "digits" as well (from their
            # ASCII value - 48).
            weight = (2 * digit) - int((digit / 5)) * 9
        else:
            # even-positioned digits just contribute their ascii
            # value minus 48
            weight = digit

        # keep a running total of weights
        sum += weight

    # avoid sum less than 10 (if characters below "0" allowed,
    # this could happen)
    sum = abs(sum) + 10

    # check digit is amount needed to reach next number
    # divisible by ten. Return an integer
    return int((10 - (sum % 10)) % 10)


def fn_next_string(doc,s):
    #This function would increase the serial number by One following the
    #alpha-numeric rules as well
    if len(s) == 0:
        return '1'
    head = s[0:-1]
    tail = s[-1]
    if tail == 'Z':
        return fn_next_string(doc, head) + '0'
    if tail == '9':
        return head+'A'
    if tail == 'H':
        return head+'J'
    if tail == 'N':
        return head+'P'
    return head + chr(ord(tail)+1)
