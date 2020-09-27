# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def validate(doc, method):
    template_doc = frappe.get_doc("Sales Taxes and Charges Template", doc.taxes_and_charges)
    validate_address_google_update(doc)
    validate_other_fields(doc)
    check_customs_tariff(doc)
    check_local_natl_tax_rules(doc, template_doc)
    check_taxes_integrity(doc, method, template_doc)


def on_update(doc, method):
    populate_item_synopsis(doc)


def check_local_natl_tax_rules(doc, template_doc):
    # Check if Shipping State is Same as Template State then check if the tax template is LOCAL
    # Else if the States are different then the template should NOT BE LOCAL
    bill_state = frappe.db.get_value("Address", doc.customer_address, "state_rigpl")
    ship_country = frappe.db.get_value("Address", doc.shipping_address_name, "country")

    if bill_state == template_doc.state and template_doc.is_export == 0:
        if template_doc.is_local_sales != 1:
            frappe.throw("Selected Tax {0} is NOT LOCAL Tax but Billing Address is in Same State {1}, "
                         "hence either change Billing Address or Change the Selected Tax".
                         format(doc.taxes_and_charges, bill_state))
    elif ship_country == 'India' and bill_state != template_doc.state:
        if template_doc.is_local_sales == 1:
            frappe.throw("Selected Tax {0} is LOCAL Tax but Billing Address is in Different State {1}, "
                         "hence either change Billing Address or Change the Selected Tax".
                         format(doc.taxes_and_charges, bill_state))
    elif ship_country != 'India':  # Case of EXPORTS
        if template_doc.is_export != 1:
            frappe.throw("Selected Tax {0} is for Indian Sales but Billing Address is in Different Country {1}, "
                         "hence either change Billing Address or Change the Selected Tax".
                         format(doc.taxes_and_charges, ship_country))


def check_customs_tariff(doc):
    for items in doc.items:
        custom_tariff = frappe.db.get_value("Item", items.item_code, "customs_tariff_number")
        if custom_tariff:
            if len(custom_tariff) == 8:
                items.gst_hsn_code = custom_tariff
            else:
                frappe.throw(("Item Code {0} in line# {1} has a Custom Tariff {2} which not 8 digit, "
                              "please get the Custom Tariff corrected"). \
                             format(items.item_code, items.idx, custom_tariff))
        else:
            frappe.throw("Item Code {0} in line# {1} does not have linked Customs Tariff in Item Master".
                         format(items.item_code, items.idx))


def validate_other_fields(doc):
    validate_add_fields(doc)
    validate_export_bill_fields(doc)
    populate_item_synopsis(doc)


def populate_item_synopsis(doc):
    it_list = []
    for item in doc.items:
        if item.idx == 1:
            it_list = update_item_table(it_list, item)
        else:
            found = 0
            for d in it_list:
                if found == 0:
                    if d.gst_hsn_code == item.gst_hsn_code and d.stock_uom == item.stock_uom:
                        d["qty"] = d["qty"] + item.qty
                        d["amount"] = d["amount"] + item.amount
                        d["base_amount"] = round(d["base_amount"] + item.base_amount, 2)
                        d["rate"] = round(d["amount"] / d["qty"], 2)
                        d["base_rate"] = round(d["base_amount"] / d["qty"], 2)
                        found = 1
                        break
            if found == 0:
                it_list = update_item_table(it_list, item)
    if not doc.items_synopsis:
        for d in it_list:
            doc.append("items_synopsis", d.copy())


def update_item_table(it_list, item_row):
    it_dict = frappe._dict({})
    it_dict["item_code"] = item_row.item_code
    it_dict["description"] = item_row.description
    it_dict["qty"] = item_row.qty
    it_dict["uom"] = item_row.uom
    it_dict["conversion_factor"] = item_row.conversion_factor
    it_dict["gst_hsn_code"] = item_row.gst_hsn_code
    it_dict["stock_uom"] = item_row.stock_uom
    it_dict["amount"] = item_row.amount
    it_dict["base_amount"] = round(item_row.base_amount, 2)
    it_dict["base_rate"] = round(it_dict["base_amount"] / it_dict["qty"], 2)
    it_dict["rate"] = round(it_dict["amount"] / it_dict["qty"], 2)
    it_dict["income_account"] = item_row.income_account
    it_dict["cost_center"] = item_row.cost_center
    it_dict["expense_account"] = item_row.expense_account
    it_list.append(it_dict.copy())
    return it_list


def validate_export_bill_fields(doc):
    tx_tmp_doc = frappe.get_doc('Sales Taxes and Charges Template', doc.taxes_and_charges)
    ship_add_doc = frappe.get_doc('Address', doc.shipping_address_name)
    if tx_tmp_doc.is_export == 1 and tx_tmp_doc.is_sample != 1:
        if not ship_add_doc.airport and doc.mode_of_transport == 'Air':
            frappe.throw('Airport is Needed for {} in {}'.
                         format(frappe.get_desk_link('Address', doc.shipping_address_name),
                                frappe.get_desk_link(doc.doctype, doc.name)))
        if not ship_add_doc.sea_port and doc.mode_of_transport == 'Ship':
            frappe.throw('Sea Port is Needed for {} in {}'.
                         format(frappe.get_desk_link('Address', doc.shipping_address_name),
                                frappe.get_desk_link(doc.doctype, doc.name)))
        if doc.mode_of_transport not in ('Air', 'Ship'):
            frappe.throw('Only Air or Sea as Mode of Transport is Allowed for Export Related {}'.
                         format(frappe.get_desk_link(doc.doctype, doc.name)))
        if not doc.export_invoice_no:
            frappe.throw('Export Invoice No is Mandatory for {}'.format(frappe.get_desk_link(doc.doctype,
                                                                                             doc.name)))
        doc.gst_category = 'Overseas'
        if not tx_tmp_doc.iec_code:
            frappe.throw('IEC Code is not Mentioned in {} for {}'.
                         format(frappe.get_desk_link('Sales Taxes and Charges Template', doc.taxes_and_charges),
                                frappe.get_desk_link(doc.doctype, doc.name)))
        if not tx_tmp_doc.bank_ad_code:
                frappe.throw('Bank AD Code is not Mentioned in {} for {}'.format(
                    frappe.get_desk_link('Sales Taxes and Charges Template', doc.taxes_and_charges),
                    frappe.get_desk_link(doc.doctype, doc.name)))
        if not tx_tmp_doc.bank_ifsc_code:
            frappe.throw('Bank IFSC Code is not Mentioned in {} for {}'.
                         format(frappe.get_desk_link('Sales Taxes and Charges Template', doc.taxes_and_charges),
                                frappe.get_desk_link(doc.doctype, doc.name)))
        if not tx_tmp_doc.export_type:
            frappe.throw('Export Type is not Mentioned in {} for {}'.
                         format(frappe.get_desk_link('Sales Taxes and Charges Template', doc.taxes_and_charges),
                                frappe.get_desk_link(doc.doctype, doc.name)))
        doc.export_type = tx_tmp_doc.export_type


def validate_add_fields(doc):
    ship_pincode = frappe.db.get_value("Address", doc.shipping_address_name, "pincode")
    bill_pincode = frappe.db.get_value("Address", doc.customer_address, "pincode")
    ship_gstin = frappe.db.get_value("Address", doc.shipping_address_name, "gstin")
    bill_gstin = frappe.db.get_value("Address", doc.customer_address, "gstin")

    if ship_pincode is None:
        frappe.throw("Shipping Pincode is Mandatory or NA, please correct it in Shipping Address {0}".
                     format(frappe.get_desk_link('Address', doc.shipping_address_name)))

    if bill_pincode is None:
        frappe.throw("Billing Pincode is Mandatory or NA, please correct it in Billing Address {0}".
                     format(frappe.get_desk_link('Address', doc.shipping_address_name)))

    doc.shipping_address_gstin = ship_gstin
    doc.billing_address_gstin = bill_gstin


def check_taxes_integrity(doc, method, template):
    if doc.taxes:
        for tax in doc.taxes:
            check = 0
            for temp in template.taxes:
                if tax.idx == temp.idx and check == 0:
                    check = 1
                    if tax.charge_type != temp.charge_type or tax.row_id != temp.row_id or \
                            tax.account_head != temp.account_head or tax.included_in_print_rate \
                            != temp.included_in_print_rate or tax.rate != temp.rate:
                        frappe.throw("Selected Tax {0}'s table does not match with tax table of Invoice# {1}. "
                                     "Check Row # {2} or reload Taxes".format(doc.taxes_and_charges, doc.name, tax.idx))
            if check == 0:
                frappe.throw("Selected Tax {0}'s table does not match with tax table of Invoice# {1}. "
                             "Check Row # {2} or reload Taxes".format(doc.taxes_and_charges, doc.name, tax.idx))
    else:
        frappe.throw("Empty Tax Table is not Allowed for Sales Invoice {0}".format(doc.name))


def validate_address_google_update(doc):
    bill_to_add_doc = frappe.get_doc('Address', doc.customer_address)
    ship_to_add_doc = frappe.get_doc('Address', doc.shipping_address_name)
    validate_address(bill_to_add_doc)
    validate_address(ship_to_add_doc)


def validate_address(add_doc):
    if not add_doc.json_reply and add_doc.dont_update_from_google != 1:
        frappe.throw(
            'Address {} is Not Updated from Google, Please Open and Save the Address once'.format(add_doc.name))
