from __future__ import unicode_literals
import frappe

def execute():
	pi_list = frappe.db.sql("""SELECT name, taxes_and_charges, supplier_address, 
		shipping_address, place_of_supply
		FROM `tabPurchase Invoice` 
		ORDER BY posting_date DESC""",as_dict=1)
	for pi in pi_list:
		if pi.supplier_address:
			sup_add_gstin = frappe.db.get_value("Address", pi.supplier_address, "gstin")
			if pi.supplier_gstin != sup_add_gstin:
				frappe.db.set_value("Purchase Invoice", pi.name, "supplier_gstin", sup_add_gstin)
				frappe.db.commit()
				print("Updated PI# " + pi.name + " Updated Supplier GSTIN to " \
					+ str(sup_add_gstin))
		if pi.shipping_address:
			comp_add_gstin = frappe.db.get_value("Address", pi.shipping_address, "gstin")
			if pi.company_gstin != comp_add_gstin:
				frappe.db.set_value("Purchase Invoice", pi.name, "company_gstin", comp_add_gstin)
				frappe.db.commit()
				print("Updated PI# " + pi.name + " Updated Company GSTIN to " \
					+ str(comp_add_gstin))
		if pi.taxes_and_charges:
			tax_temp_doc = frappe.get_doc("Purchase Taxes and Charges Template", pi.taxes_and_charges)
			if pi.place_of_supply != tax_temp_doc.state:
				frappe.db.set_value("Purchase Invoice", pi.name, "place_of_supply", tax_temp_doc.state)
				frappe.db.commit()
				print("Updated PI# " + pi.name + " Changed Place of Supply to " \
					+ str(tax_temp_doc.state))