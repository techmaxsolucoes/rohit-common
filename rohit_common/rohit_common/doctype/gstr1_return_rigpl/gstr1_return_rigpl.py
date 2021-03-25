# -*- coding: utf-8 -*-
# Copyright (c) 2021, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from datetime import datetime
from frappe.model.document import Document
from frappe.utils import getdate
from erpnext.accounts.utils import get_fiscal_year
from ....utils.common import update_child_table
from ....utils.rohit_common_utils import check_dynamic_link
from ....utils.accounts_utils import get_base_doc_no, get_taxes_from_sid, get_gst_si_type, get_gst_export_fields, \
    get_gst_jv_type, get_taxes_from_jvd, get_linked_type_from_jv, get_hsn_sum_frm_si, get_inv_status, \
    get_invoice_uploader
from ...india_gst_api.common import gst_return_period_validation, get_dates_from_return_period
from ...india_gst_api.gst_api import get_gstr1
from ...india_gst_api.gst_public_api import track_return, get_arn_status

gstr1_actions = [
    {"action": "AT", "name": "Advances Tax", "tbl": "at_invoices"},
    {"action": "ATA", "name": "Advances Tax Amendments", "tbl": "ataa_invoices"},
    {"action": "B2B", "name": "B2B", "tbl": "b2b_invoices"},
    {"action": "B2BA", "name": "B2B Amendments", "tbl": "b2ba_invoices"},
    {"action": "B2CL", "name": "B2BC Large", "tbl": "b2cl_invoices"},
    {"action": "B2CLA", "name": "B2C Large Amendments", "tbl": "b2cla_invoices"},
    {"action": "B2CS", "name": "B2C Small", "tbl": "b2cs_invoices"},
    {"action": "B2CSA", "name": "B2C Small Amendments", "tbl": "b2csa_invoices"},
    {"action": "CDNR", "name": "CDN Registered", "tbl": "cdb_b2b"},
    {"action": "CDNRA", "name": "CDN Registered Amendments", "tbl": "cdb_b2ba"},
    {"action": "CDNUR", "name": "CDN Un-Registered", "tbl": "cdn_b2c"},
    {"action": "CDNURA", "name": "CDN Un=Registered Amendments", "tbl": "cdn_b2ca"},
    {"action": "DOCISS", "name": "Docs Issued", "tbl": "docs_issued"},
    {"action": "EINV", "name": "e-Invoices", "tbl": "einv"},
    {"action": "EXP", "name": "Export Invoices", "tbl": "export_invoices"},
    {"action": "EXPA", "name": "Export Invoices Amendments", "tbl": "export_amend"},
    {"action": "HSNSUM", "name": "GSTR1 HSN Summary", "tbl": "hsn_sum"},
    {"action": "NIL", "name": "Nil Supplies", "tbl": "nil_sup"},
    {"action": "TXP", "name": "Tax Paid", "tbl": "adv_adj"},
    {"action": "TXPA", "name": "Tax Paid Amendments", "tbl": "adv_adja"}
]

# {"action": "RETSTATUS", "name": "GSTR1 Status", "tbl": "none"}
# {"action": "RETSUM", "name": "GSTR1 Summary", "tbl": "none"}
# {"action": "RETSUBMIT", "name": "Submit GSTR1", "tbl": "none"}
# {"action": "RESET", "name": "Reset GSTR1"}
# {"action": "RESTSAVE", "name": "Save GSTR1"}


class GSTR1ReturnRIGPL(Document):

    def generate_synopsis(self):
        syn_txt = ""
        si_tables = [{"tbl": "b2b_invoices", "name": "B2B Invoices"},
                     {"tbl": "b2cl_invoices", "name": "B2C Large Invoices"},
                     {"tbl": "cdn_b2b", "name": "Credit/ Debit Notes (Registered)"},
                     {"tbl": "cdn_b2c", "name": "Credit/ Debit Notes (Un-Registered)"},
                     {"tbl": "export_invoices", "name": "Export Invoices"},
                     {"tbl": "b2c_invoices", "name": "B2C Invoices"}]
        for txt in si_tables:
            tot_docs, inv_val, tax_val, igst, sgst, cgst = 0, 0, 0, 0, 0, 0
            syn_txt += f"<br> <b>{txt.get('name')} </b><br>"
            if self.get(txt.get("tbl")):
                for row in self.get(txt.get("tbl")):
                    tot_docs += 1
                    inv_val += row.total_invoice_value
                    tax_val += row.taxable_value
                    igst += row.igst
                    sgst += row.sgst
                    cgst += row.cgst
                syn_txt += f"Total Documents = {tot_docs} <br>" \
                           f"Total Value = {round(inv_val,2)} <br>Total Taxable Value = {round(tax_val,2)} <br>" \
                           f"Total Tax Liability = {round(igst+cgst+sgst,2)} <br>Total IGST = {round(igst,2)} <br>" \
                           f"Total SGST = {round(sgst,2)} <br>Total CGST = {round(cgst,2)}"
            syn_txt += "<hr>"
        self.synopsis_text = syn_txt

    def generate_hsn_summary(self):
        self.set("hsn_summary", [])
        si_tables = ["b2b_invoices", "b2cl_invoices", "cdn_b2c", "cdn_b2b", "export_invoices", "b2c_invoices"]
        hsn_list = []
        for tbl in si_tables:
            if self.get(tbl):
                for row in self.get(tbl):
                    if row.document_type == "Sales Invoice":
                        hsn_sum = get_hsn_sum_frm_si(row.document_number)
                        if hsn_list:
                            for hsn in hsn_sum:
                                found = 0
                                for base_hsn in hsn_list:
                                    if base_hsn.hsn == hsn.hsn and base_hsn.uom == hsn.uom:
                                        found = 1
                                        base_hsn.total_quantity += hsn.total_quantity
                                        base_hsn.total_taxable_value += hsn.total_taxable_value
                                        base_hsn.igst += hsn.igst
                                        base_hsn.cgst += hsn.cgst
                                        base_hsn.sgst += hsn.sgst
                                        base_hsn.cess += hsn.cess
                                        base_hsn.total_value += hsn.total_value
                                if found == 0:
                                    hsn_list.append(hsn.copy())
                        else:
                            for hsn in hsn_sum:
                                hsn_list.append(hsn.copy())
        # frappe.msgprint(str(hsn_list))
        hsn_list = sorted(hsn_list, key=lambda i: i["hsn"], reverse=0)
        update_child_table(doc=self, table_name="hsn_summary", row_list=hsn_list)

    def clear_all_tables(self):
        si_tables = ["b2b_invoices", "b2cl_invoices", "cdn_b2c", "cdn_b2b", "export_invoices", "b2c_invoices",
                     "hsn_summary"]
        self.synopsis_text = ""
        for si in si_tables:
            self.set(si, [])

    def get_gstr1_details(self):
        if self.is_new() == 1:
            frappe.throw("Save the document before Getting GSTR1 Data")
        first_date_text = "01-" + self.return_period[:2] + "-" + self.return_period[2:]
        fy = get_fiscal_year(date=getdate(first_date_text))
        if not self.arn_number:
            # If GSTR1 is not Filed then Check if Filed and if Filed then get the ARN and other details and verify
            # from GST Network
            return_status = track_return(gstin=self.gstin, fiscal_year=fy[0], type_of_return="R1")
            self.arn_number, self.filing_status, self.filing_date, self.mode_of_filing = \
                get_arn_status(ret_status_json=return_status, type_of_return="GSTR1", ret_period=self.return_period)
            # If the GSTR1 is not filed then SAVE the data after validation of the data on GSTN Portal
        else:
            # If GSTR1 arn is there then verify the data with generated GSTR1
            # gstr1_actions = [{"action": "B2B", "name": "B2B", "tbl": "b2b_invoices"}]
            for act_dict in gstr1_actions:
                resp = get_gstr1(gstin=self.gstin, ret_period=self.return_period, action="B2B")
                # resp = json.loads(self.json_reply.replace("'", '"'))
                if not resp:
                    frappe.msgprint(f"<b>{act_dict.get('name')}</b> there is Some Error or No Data "
                                    f"for {self.return_period}")
                else:
                    frappe.msgprint(f"<b>{act_dict.get('name')}</b> for Period {self.return_period} is Fetched")
                    self.process_gstr1(response=resp, act_dict=act_dict)

    def process_gstr1(self, response, act_dict):
        action = act_dict.get("action")
        act_desc = act_dict.get("name")
        resp_data = response.get(action.lower())
        if not self.get(act_dict.get("tbl"), []):
            if resp_data:
                frappe.throw(f"For {act_desc} there is Data in GST Network but Table for the Same is Empty")
        else:
            if not resp_data:
                frappe.throw(f"For {act_desc} there is No Data in GST Network but Table for the Same has Data")
            else:
                for d in response.get(action.lower()):
                    d = frappe._dict(d)
                    match_and_update_details_from_gstin(d, self, act_dict)

    def validate(self):
        gst_return_period_validation(return_period=self.return_period)
        self.validate_si_tables()
        self.generate_synopsis()
        self.generate_hsn_summary()

    def on_submit(self):
        self.validate_export_invoices()
        self.validate_si_tables(submit=1)
        frappe.throw("Submission is Not Allowed for the Time Being")

    def validate_si_tables(self, submit=0):
        si_tables = ["b2b_invoices", "b2cl_invoices", "cdn_b2c", "cdn_b2b", "export_invoices", "b2c_invoices"]
        if self.filing_status == "Filed":
            filed = 1
        else:
            filed = 0
        for tbl in si_tables:
            for d in self.get(tbl):
                if filed == 1:
                    if not d.invoice_checksum:
                        message = f"For Row# {d.idx} the Invoice Checksum is Not Mentioned but Return is Filed so " \
                                  f"you wont be able to Submit the Document. Pull the Data from GSTIN Network to Submit"
                        if submit == 1:
                            frappe.throw(message)
                        else:
                            frappe.msgprint(message)
                if d.document_type == "Sales Invoice":
                    d.receiver_address = frappe.get_value(d.document_type, d.document_number, "customer_address")
                    d.receiver_gstin = frappe.get_value(d.document_type, d.document_number, "billing_address_gstin")
                elif d.document_type == "Journal Entry":
                    link_dt, link_dn = get_linked_type_from_jv(jv_name=d.document_number)
                    check_dynamic_link(parenttype="Address", parent=d.receiver_address, link_doctype=link_dt,
                                       link_name=link_dn)
                    d.receiver_gstin = frappe.get_value("Address", d.receiver_address, "gstin")
                else:
                    frappe.throw(f"{d.document_type} mentioned in Row# {d.idx} is Not Supported")
                d.receiver_name = frappe.get_value("Address", d.receiver_address, "address_title")

    def validate_export_invoices(self):
        for d in self.export_invoices:
            if not d.gst_payment or not d.port_code or not d.shipping_bill_no or not d.shipping_bill_date:
                frappe.throw(f"For Row# {d.idx} in Export Invoices either GST Payment or Port Code or SHB Details "
                             f"are not mentioned.")

    def get_details(self):
        self.clear_all_tables()
        self.generate_gstr1()

    def generate_gstr1(self):
        frm_dt, to_dt = get_dates_from_return_period(self.return_period)
        self.get_invoices(start_date=frm_dt, end_date=to_dt)
        self.get_jv_entries(start_date=frm_dt, end_date=to_dt)
        frappe.msgprint("Updated All Tables")

    def get_jv_entries(self, start_date, end_date):
        gst_set = frappe.get_doc("GST Settings", "GST Setting")
        gst_acc = []
        cdn_b2b_list = []
        for d in gst_set.gst_accounts:
            gst_acc.append(d.cgst_account)
            gst_acc.append(d.sgst_account)
            gst_acc.append(d.igst_account)
            gst_acc.append(d.cess_account)
        jv_dict = frappe.db.sql("""SELECT jv.name, jvd.account 
        FROM `tabJournal Entry` jv, `tabJournal Entry Account` jvd 
        WHERE jvd.parent = jv.name AND jv.docstatus=1 AND jv.posting_date >= '%s' AND jv.posting_date <= '%s' 
        ORDER BY jv.posting_date, jv.name, jvd.idx""" % (start_date, end_date), as_dict=1)
        jv_templ_list = []
        for jv in jv_dict:
            if jv.account in gst_acc:
                jv_templ_list.append(jv.name)
        jv_list = []
        for i in jv_templ_list:
            if i not in jv_list:
                jv_list.append(i)
        # Above list is of all JV in period where GST Accounts are there. Now JV would be Credit or Debit if it has
        # Creditor or Debtor as a Row in JV Accounts
        jv_cdn = []
        for jv in jv_list:
            jvd = frappe.get_doc("Journal Entry", jv)
            for acc in jvd.accounts:
                if acc.party_type == "Customer" and jvd.name not in jv_cdn:
                    jv_cdn.append(jv)
        for jv in jv_cdn:
            row = get_row_from_jv_name(jv)
            cdn_b2b_list.append(row.copy())
        update_child_table(doc=self, table_name="cdn_b2b", row_list=cdn_b2b_list)

    def get_invoices(self, start_date, end_date):
        inv_list = frappe.db.sql("""SELECT name FROM `tabSales Invoice` WHERE docstatus = 1 AND posting_date >= '%s' 
        AND posting_date <= '%s' AND company_gstin = '%s' 
        ORDER BY customer, name""" % (start_date, end_date, self.gstin), as_dict=1)
        b2b_list = []
        b2cl_list = []
        b2c_list = []
        exp_list = []
        cdn_b2b_list = []
        cdn_b2c_list = []
        for inv in inv_list:
            row = get_row_from_inv_name(inv.name)
            if row:
                if row["invoice_type_2"] == "b2b":
                    b2b_list.append(row.copy())
                elif row["invoice_type_2"] == "b2cl":
                    b2cl_list.append(row.copy())
                elif row["invoice_type_2"] == "b2c":
                    b2c_list.append(row.copy())
                elif row["invoice_type_2"] == "export":
                    exp_list.append(row.copy())
                elif row["invoice_type_2"] == "cdn_b2c":
                    cdn_b2c_list.append(row.copy())
                elif row["invoice_type_2"] == "cdn_b2b":
                    cdn_b2b_list.append(row.copy())
                else:
                    frappe.throw(f"Unknown Invoice Type for {row.document_number}")
        update_child_table(doc=self, table_name="b2b_invoices", row_list=b2b_list)
        update_child_table(doc=self, table_name="b2cl_invoices", row_list=b2cl_list)
        update_child_table(doc=self, table_name="b2c_invoices", row_list=b2c_list)
        update_child_table(doc=self, table_name="export_invoices", row_list=exp_list)
        update_child_table(doc=self, table_name="cdn_b2b", row_list=cdn_b2b_list)
        update_child_table(doc=self, table_name="cdn_b2c", row_list=cdn_b2c_list)


def match_and_update_details_from_gstin(gstin_resp, gstr1_doc, act_dict):
    # frappe.msgprint(f"Checking for GSTIN: {gstin_resp.ctin}")
    si_gstin = frappe.db.sql("""SELECT * FROM `tabGSTR1 Return Invoices` WHERE parent = '%s' AND parenttype = '%s'
    AND parentfield = '%s' AND receiver_gstin = '%s' ORDER BY idx""" %
                             (gstr1_doc.name, gstr1_doc.doctype, act_dict.get("tbl"), gstin_resp.ctin), as_dict=1)
    if len(si_gstin) > 0:
        if len(si_gstin) != len(gstin_resp.inv):
            frappe.throw(f"For GSTIN: {gstin_resp.ctin} Total Invoices in GST= {len(gstin_resp.inv)} Whereas in "
                         f"System the Total Invoices = {len(si_gstin)}.<br>Please Correct the Error to Proceed")
        for inv in gstin_resp.inv:
            # frappe.msgprint(f"Checking for Invoice # {inv.get('inum')}")
            inv_found = 0
            for row in si_gstin:
                if inv.get("inum") == row.document_number or inv.get("inum") == row.invoice_number:
                    inv_found = 1
                    gst_inv_date = datetime.strptime(inv.get("idt"), "%d-%m-%Y").date()
                    if inv.get("val") != row.total_invoice_value:
                        frappe.throw(f"For Row# {row.idx} Total Invoice Value does "
                                     f"not Match with GST Network Inv Value <b>{inv.get('val')}</b>")
                    elif gst_inv_date != getdate(row.invoice_date):
                        frappe.throw(f"For Row# {row.idx} Invoice Date does not Match with GST Network "
                                     f"Inv Date <b>{gst_inv_date}</b>")
                    else:
                        frappe.db.set_value("GSTR1 Return Invoices", row.name, "invoice_status",
                                            get_inv_status(inv.get('flag')))
                        frappe.db.set_value("GSTR1 Return Invoices", row.name, "uploaded_by",
                                            get_invoice_uploader(inv.get('updby')))
                        frappe.db.set_value("GSTR1 Return Invoices", row.name, "invoice_checksum", inv.get("chksum"))
                        # row.invoice_status = get_inv_status(inv.get('flag'))
                        # row.uploaded_by = get_invoice_uploader(inv.get('updby'))
                        # row.invoice_checksum = inv.get("chksum")
        if inv_found != 1:
            frappe.throw(f"For GSTIN: {gstin_resp.ctin} and Inv# {row.document_number} is Not Found")
    else:
        frappe.throw(f"GSTIN:{gstin_resp.ctin} is Not Found in Table for {act_dict}")


def get_row_from_jv_name(jv_name):
    row = frappe._dict({})
    jvd = frappe.get_doc("Journal Entry", jv_name)
    jv_type = get_gst_jv_type(jvd)
    if jv_type == "credit":
        note_type = "Credit"
    else:
        note_type = "Debit"
    tax_rate, sgst_amt, cgst_amt, igst_amt, cess_amt, net_amt = get_taxes_from_jvd(jvd, jv_type)
    row["is_credit_debit"] = 1
    row["note_type"] = note_type
    row["document_type"] = "Journal Entry"
    row["document_number"] = jvd.name
    row["invoice_number"] = get_base_doc_no(jvd)
    row["invoice_date"] = jvd.posting_date
    row["total_invoice_value"] = jvd.total_debit
    row["taxable_value"] = net_amt
    row["rate"] = tax_rate
    row["igst"] = igst_amt
    row["sgst"] = sgst_amt
    row["cgst"] = cgst_amt
    return row


def get_row_from_inv_name(inv_name):
    row = frappe._dict({})
    multi_factor = 1
    sid = frappe.get_doc("Sales Invoice", inv_name)
    inv_type = get_gst_si_type(sid)
    if inv_type == "cdn_b2b" or inv_type == "cdn_b2c":
        row["is_credit_debit"] = 1
        row["note_type"] = "Credit"
        multi_factor = -1

    elif inv_type == "export":
        row["export_sales"] = 1
        row["shipping_bill_no"], row["shipping_bill_date"], row["gst_payment"], row["port_code"] = \
            get_gst_export_fields(sid)
    bad_doc = frappe.get_doc("Address", sid.customer_address)
    base_inv_no = get_base_doc_no(sid)
    tax_rate, sgst_amt, cgst_amt, igst_amt, cess_amt = get_taxes_from_sid(sid)
    row["invoice_type_2"] = inv_type
    row["invoice_type"] = "R-Regular B2B Invoices" # TODO make invoice Type dynamic instead of static
    row["receiver_address"] = sid.customer_address
    row["receiver_gstin"] = sid.billing_address_gstin
    row["document_type"] = "Sales Invoice"
    row["document_number"] = sid.name
    row["invoice_number"] = base_inv_no
    row["receiver_name"] = bad_doc.address_title
    row["invoice_date"] = sid.posting_date
    row["total_invoice_value"] = sid.base_grand_total * multi_factor
    row["rate"] = tax_rate
    row["taxable_value"] = sid.base_net_total * multi_factor
    row["igst"] = igst_amt * multi_factor
    row["sgst"] = sgst_amt * multi_factor
    row["cgst"] = cgst_amt * multi_factor
    return row
