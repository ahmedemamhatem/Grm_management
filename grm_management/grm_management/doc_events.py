# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def populate_code_from_name(doc, method):
	"""Populate code field from auto-generated name"""

	code_field_mapping = {
		"GRM Location": "location_code",
		"GRM Property": "property_code",
		"GRM Space": "space_code",
		"GRM Space Type": "space_type_code",
		"GRM Landlord": "landlord_code",
		"GRM Property Contract": "contract_number",
		"GRM Tenant": "tenant_code"
	}

	if doc.doctype in code_field_mapping:
		code_field = code_field_mapping[doc.doctype]
		if hasattr(doc, code_field) and not getattr(doc, code_field):
			setattr(doc, code_field, doc.name)
