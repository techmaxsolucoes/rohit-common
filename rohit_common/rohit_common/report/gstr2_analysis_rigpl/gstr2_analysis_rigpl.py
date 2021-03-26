#  Copyright (c) 2021. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data = []
	cond = get_conditions(filters)
	gst_set = frappe.get_doc("GST Settings", "GST Setting")
	gst_taxes = []
	for d in gst_set.gst_accounts:
		if d.get("cgst_account", "") and "Input" in d.get("cgst_account", "No"):
			gst_taxes.append(d.cgst_account)
		if d.get("sgst_account", "") and  "Input" in d.get("sgst_account", "No"):
			gst_taxes.append(d.sgst_account)
		if d.get("igst_account", "") and "Input" in d.get("igst_account", "No"):
			gst_taxes.append(d.igst_account)
		if d.get("cess_account", "") and "Input" in d.get("cess_account", "No"):
			gst_taxes.append(d.cess_account)
	for tax in gst_taxes:
		gl_entries = get_gl_entries(tax, cond)
		for gl in gl_entries:
			gl = get_party_details(gl)
			gl = get_gstr2_details(gl)
			cgst, sgst, igst, cess = 0, 0, 0, 0
			if "CGST" in tax:
				if gl.debit > 0:
					cgst = gl.debit
				else:
					cgst = -1 * gl.credit
			if "IGST" in tax:
				if gl.debit > 0:
					igst = gl.debit
				else:
					igst = -1 * gl.credit
			if "SGST" in tax:
				if gl.debit > 0:
					sgst = gl.debit
				else:
					sgst = -1 * gl.credit
			if "CESS" in tax:
				if gl.debit > 0:
					cess = gl.debit
				else:
					cess = -1 * gl.credit
			gstr2_tot_tax = gl.get("gstr2_igst", 0) + gl.get("gstr2_cgst", 0) + gl.get("gstr2_sgst", 0) + \
							gl.get("gstr2_cess", 0)
			doc_tot_tax = igst + cgst + sgst + cess
			row = [gl.posting_date, gl.voucher_no, gl.get("party", ""),
				   gl.get("gstr1_stat", 0), gl.get("gstr1_fil_date", "1900-01-01"),
				   gl.get("period_gstr1", ""), gl.get("gstr3b_stat", 0),
				   gl.get("party_gstin", ""), gl.get("note_type", "X"), gl.get("sup_inv_no", ""),
				   gl.get("sup_inv_date", "1900-01-01"),
				   gl.get("gstr2_gt", 0), gl.get("gstr2_nt", 0), gl.get("gstr2_igst", 0), gl.get("gstr2_cgst", 0),
				   gl.get("gstr2_sgst", 0), gl.get("gstr2_cess", 0), gstr2_tot_tax, gl.get("doc_gt", 0),
				   gl.get("doc_nt", 0), igst, cgst, sgst, cess, doc_tot_tax, gl.voucher_type, gl.get("party_type", "")]
			data.append(row)
	return data


def get_gstr2_details(gl):
	cond = ""
	cond_or = ""
	if gl.voucher_type == "Purchase Invoice":
		cond_or += f" AND (gstri.supplier_invoice_no = '{gl.sup_inv_no}' OR " \
				   f"gstri.linked_document_name = '{gl.voucher_no}')"
		self_add = frappe.get_value(gl.voucher_type, gl.voucher_no, "shipping_address")
		self_gstin = frappe.get_value("Address", self_add, "gstin")
		cond += f" AND gstr.gstin = '{self_gstin}'"
		cond += f" AND gstri.party = '{gl.party}' AND gstri.party_type = '{gl.party_type}'"
	else:
		cond += f" AND gstri.linked_document_type = '{gl.voucher_type}' AND " \
				f"gstri.linked_document_name = '{gl.voucher_no}'"

	query = """SELECT gstr.name, gstri.filing_status_gstr1, gstri.filing_date_gstr1, gstri.filing_status_gstr3b,
	gstri.filing_period_gstr1, gstri.note_type, gstri.grand_total, gstri.taxable_value, gstri.cgst_amount, 
	gstri.sgst_amount, gstri.igst_amount, gstri.cess_amount, gstri.supplier_invoice_no, gstri.supplier_invoice_date,
	gstri.party_gstin
	FROM `tabGSTR2A RIGPL` gstr, `tabGSTR2 Return Invoices` gstri
	WHERE gstr.docstatus != 2 AND gstri.parent = gstr.name %s %s""" % (cond, cond_or)
	gstr2a_list = frappe.db.sql(query, as_dict=1)
	if gstr2a_list:
		gl["gstr1_stat"] = gstr2a_list[0].filing_status_gstr1
		if gstr2a_list[0].note_type == "Bill of Entry":
			gl["gstr3b_stat"] = 1
			gl["gstr1_fil_date"] = gstr2a_list[0].supplier_invoice_date
			gl["sup_inv_date"] = gstr2a_list[0].supplier_invoice_date
			gl["sup_inv_no"] = gstr2a_list[0].supplier_invoice_no
			gl["party_gstin"] = gstr2a_list[0].party_gstin
		else:
			gl["gstr3b_stat"] = gstr2a_list[0].filing_status_gstr3b
			gl["gstr1_fil_date"] = gstr2a_list[0].filing_date_gstr1

		gl["period_gstr1"] = gstr2a_list[0].filing_period_gstr1
		gl["note_type"] = gstr2a_list[0].note_type
		gl["gstr2_gt"] = gstr2a_list[0].grand_total
		gl["gstr2_nt"] = gstr2a_list[0].taxable_value
		gl["gstr2_cgst"] = gstr2a_list[0].cgst_amount
		gl["gstr2_sgst"] = gstr2a_list[0].sgst_amount
		gl["gstr2_igst"] = gstr2a_list[0].igst_amount
		gl["gstr2_cess"] = gstr2a_list[0].cess_amount
	return gl


def get_party_details(gl_dict):
	pid = frappe.get_doc(gl_dict.voucher_type, gl_dict.voucher_no)
	if gl_dict.voucher_type == "Purchase Invoice":
		gl_dict["party_type"] = "Supplier"
		gl_dict["party"] = pid.supplier
		gl_dict["party_gstin"] = pid.supplier_gstin
		gl_dict["sup_inv_no"] = pid.bill_no
		gl_dict["sup_inv_date"] = pid.bill_date
		gl_dict["doc_gt"] = pid.base_grand_total
		gl_dict["doc_nt"] = pid.base_net_total
	else:
		gl_dict["doc_gt"] = pid.total_debit
	return gl_dict


def get_gl_entries(tax, conditions):
	cond_acc = f" AND gl.account = '{tax}'"
	gl_map = frappe.db.sql("""SELECT gl.name, gl.posting_date, gl.account, gl.debit_in_account_currency as debit, 
	gl.credit_in_account_currency as credit, gl.voucher_type, gl.voucher_no FROM `tabGL Entry` gl 
	WHERE docstatus = 1 %s %s ORDER BY gl.posting_date, gl.name""" % (cond_acc, conditions), as_dict=1)
	return gl_map


def get_columns(filters):
	return [
		"Posting Date:Date:80",
		{
			"label": "Voucher No",
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 130
		},
		{
			"label": "Party",
			"fieldname": "party",
			"fieldtype": "Dynamic Link",
			"options": "party_type",
			"width": 250
		},
		"GSTR1 Status:Int:30", "GSTR1 Filing Date:Date:80", "GSTR1 Period::80",
		"GSTR3B Status:Int:30", "Party GSTIN::180", "Type::80",
		"Supplier Inv#::120", "Supplier Inv Date:Date:80", "GSTR2-GT:Currency:120", "GSTR2-NT:Currency:120",
		"GSTR2-IGST:Currency:120", "GSTR2-CGST:Currency:120", "GSTR2-SGST:Currency:120", "GSTR2-Cess:Currency:120",
		"GSTR2-Total Tax:Currency:120",
		"Doc-GT:Currency:120", "Doc-NT:Currency:120", "Doc-IGST:Currency:120", "Doc-CGST:Currency:120",
		"Doc-SGST:Currency:120", "Doc-Cess:Currency:120", "Doc-Total Tax:Currency:120",
		{
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"width": 1
		},
		{
			"label": "Party Type",
			"fieldname": "party_type",
			"width": 1
		}
	]


def get_conditions(filters):
	cond = ""
	max_diff = 32
	days = (getdate(filters.get('to_date')) - getdate(filters.get('from_date'))).days
	if days <= 0:
		frappe.throw(f"To Date has to be Greater than From Date")
	elif days >= max_diff:
		frappe.throw(f"Difference between To and From Date Cannot be more than {max_diff} days")
	else:
		cond += " AND gl.posting_date >= '%s'" % filters.get("from_date")
		cond += " AND gl.posting_date <= '%s'" % filters.get("to_date")
	return cond
