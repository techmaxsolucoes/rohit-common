# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Ltd. and contributors
# For license information, please see license.txt

#This Scheduled task would list all the public and private files if the files are not in the DB `tabFiles`
#then it would delete them.


from __future__ import unicode_literals
import frappe
import os
from os import listdir
from os.path import isfile, join
from frappe.utils import get_files_path
from frappe.utils.file_manager import delete_file

def execute():
	public_files_path = get_files_path()
	private_files_path = get_files_path(is_private=1)
	print (public_files_path)
	print (private_files_path)
	public_files = [f for f in listdir(public_files_path) if isfile(join(public_files_path, f))]
	private_files = [f for f in listdir(private_files_path) if isfile(join(private_files_path, f))]
	orphan_private = 0
	orphan_pub = 0

	for list_of_files in [public_files, private_files]:
		if list_of_files:
			for files in list_of_files:
				if list_of_files == public_files:
					file_path = public_files_path + '/' + files
				else:
					file_path = private_files_path + '/' + files

				file_db = frappe.db.sql("""SELECT name, attached_to_doctype, attached_to_name, file_url, file_name 
					FROM `tabFile` WHERE  file_name = '%s'"""%(files), as_list=1)
				if file_db:
					pass
					#print(file_db)
				else:
					#delete_file(file_path)
					print("Deleted file with Name = " + files + " and file path = " + file_path)
					if list_of_files == public_files:
						orphan_pub += 1
					else:
						orphan_private += 1

					print("Orphaned File Name = " + files + " path = " + file_path)
	print ("Public Files Orphaned and hence Deleted = " + str(orphan_pub))
	print ("Private Files Orphaned and hence Deleted = " + str(orphan_private))