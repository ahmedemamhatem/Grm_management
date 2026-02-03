# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, validate_email_address

class GRMLandlord(Document):
	def validate(self):
		self.validate_contact_info()
		self.update_statistics()

	def after_insert(self):
		"""Auto-create ERPNext Supplier"""
		self.create_supplier()

	def validate_contact_info(self):
		"""Validate email and phone formats"""
		if self.primary_email and not validate_email_address(self.primary_email):
			frappe.throw(frappe._("Invalid email address"))

	def create_supplier(self):
		"""Auto-create ERPNext Supplier for this landlord (Tenant pays to landlord)"""
		if self.supplier:
			return

		try:
			supplier = frappe.new_doc("Supplier")
			supplier.supplier_name = self.landlord_name
			supplier.supplier_group = "Property Landlords"
			supplier.supplier_type = self.landlord_type or "Individual"

			# Add contact details
			if self.primary_email:
				supplier.email_id = self.primary_email

			if self.primary_phone:
				supplier.mobile_no = self.primary_phone

			supplier.insert(ignore_permissions=True)

			# Link supplier to landlord
			self.supplier = supplier.name
			self.save()

			frappe.msgprint(frappe._("Supplier {0} created for landlord {1}").format(supplier.name, self.landlord_name))
		except Exception as e:
			frappe.log_error(f"Failed to create supplier for {self.name}: {str(e)}")
			frappe.msgprint(frappe._("Could not create supplier automatically. Please create manually."), indicator="orange")

	def update_statistics(self):
		"""Update statistics from related properties and contracts"""
		# Count total properties
		self.total_properties = frappe.db.count("GRM Property", {
			"landlord": self.name
		})

		# Count active contracts
		self.active_contracts = frappe.db.count("GRM Property Contract", {
			"landlord": self.name,
			"status": "Active"
		})

		# Calculate total monthly rent from active contracts
		total_rent = frappe.db.sql("""
			SELECT SUM(monthly_rent) as total
			FROM `tabGRM Property Contract`
			WHERE landlord = %s AND status = 'Active'
		""", self.name)

		self.total_monthly_rent = flt(total_rent[0][0]) if total_rent and total_rent[0][0] else 0

		# Calculate total arrears from pending Payment Entries
		if self.supplier:
			total_arrears = frappe.db.sql("""
				SELECT SUM(unallocated_amount) as total
				FROM `tabPayment Entry`
				WHERE party_type = 'Supplier'
				AND party = %s
				AND docstatus = 1
			""", self.supplier)

			self.total_arrears = flt(total_arrears[0][0]) if total_arrears and total_arrears[0][0] else 0
