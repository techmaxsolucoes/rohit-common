# Copyright (c) 2013, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	if filters.get("summary_dt")==1:
		return ["Attached to Doctype::300", "No of Files:Int:100", "Size (MB):Float:100"]
	elif filters.get("summary_fol")==1:
		return ["Attached to Doctype::300", "No of Files:Int:100", "Size (MB):Float:100"]
	else:
		if filters.get("folder") == 1:
			return [
				"ID:Link/File:150", "File Name::200", "Parent Folder::200", "Size(MB):Float:100", 
				"Left:Int:80", "Right:Int:80", "Is Home:Int:40", "Is Attachment::40" 
			]
		else:
			return [
				"ID:Link/File:150", "File Name::200", "Attached to DT::100", 
				"Attached to Name:Dynamic Link/Attached to DT:100", 
				"Size (kB):Float:100", "Left:Int:80", "Right:Int:80", "Parent Folder::100", "Private:Int:40", 
				"Owner::100", "Created On:Datetime:120", "URL::300" 
			]

def get_data(filters):
	conditions = get_conditions(filters)
	if filters.get("summary_dt")==1:
		data = frappe.db.sql("""SELECT IFNULL(attached_to_doctype, "NO DOCTYPE"), COUNT(name) as no_of_files,
			ROUND(((SUM(file_size))/1024/1024),2)
			FROM `tabFile`
			WHERE docstatus=0 AND is_folder=0 
			GROUP BY attached_to_doctype ORDER BY no_of_files DESC """, as_list=1)
	elif filters.get("summary_fol")==1:
		data = frappe.db.sql("""SELECT IFNULL(folder, "NO FOLDER"), COUNT(name) as no_of_files,
			ROUND(((SUM(file_size))/1024/1024),2)
			FROM `tabFile`
			WHERE docstatus=0 AND is_folder=0 
			GROUP BY folder ORDER BY no_of_files DESC """, as_list=1)
	else:
		if filters.get("folder") == 1:
			data = frappe.db.sql("""SELECT name, file_name, folder, ROUND(file_size/1024/1024,2), lft, rgt, 
				is_home_folder, is_attachments_folder
				FROM `tabFile` WHERE docstatus = 0 %s ORDER BY creation"""%(conditions), as_list=1)
		else:
			data = frappe.db.sql("""SELECT name, IFNULL(file_name, "NO NAME"), IFNULL(attached_to_doctype, "NO DOCTYPE"), 
				IFNULL(attached_to_name,"NO DOCNAME"),
				ROUND(file_size/1024,2), lft, rgt, IFNULL(folder, "NO FOLDER"), is_private, owner, creation, file_url
				FROM `tabFile` WHERE docstatus=0 %s ORDER BY creation"""%(conditions), as_list=1)

	return data

def get_conditions(filters):
	conditions = ""
	if filters.get("folder")==1:
		conditions += " AND is_folder=1"
	else:
		conditions += " AND is_folder=0"

	if filters.get("private")=="Only Private":
		conditions += " AND is_private=1"
	elif filters.get("private")== "Only Public":
		conditions += " AND is_private=0"
	else:
		pass

	if filters.get("dt_types")!= "None" and filters.get("doctype"):
		conditions += " AND attached_to_doctype = '%s'"%(filters.get("doctype"))
	elif filters.get("dt_types")=="None" and filters.get("doctype"):
		frappe.throw("None Doctype Selected and hence Cannot Select a Specific Doctype")
	
	if filters.get("dt_types") == "None":
		conditions += " AND attached_to_doctype IS NULL"

	return conditions
