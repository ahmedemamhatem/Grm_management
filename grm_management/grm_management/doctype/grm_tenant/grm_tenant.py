# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, validate_email_address

class GRMTenant(Document):
	def validate(self):
		self.validate_contact_info()
		self.update_statistics()

	def after_insert(self):
		"""Auto-create ERPNext Customer"""
		self.create_customer()

	def validate_contact_info(self):
		"""Validate email formats"""
		if self.primary_email and not validate_email_address(self.primary_email):
			frappe.throw(frappe._("Invalid primary email address"))

		if self.secondary_email and not validate_email_address(self.secondary_email):
			frappe.throw(frappe._("Invalid secondary email address"))

	def create_customer(self):
		"""Auto-create ERPNext Customer for this tenant (Tenant pays for subscriptions)"""
		if self.customer:
			return

		try:
			customer = frappe.new_doc("Customer")
			customer.customer_name = self.tenant_name
			customer.customer_type = self.tenant_type or "Company"

			# Set customer group based on tenant type
			if self.tenant_type == "Individual":
				customer.customer_group = "Individual"
			elif self.tenant_type == "Government":
				customer.customer_group = "Government"
			else:
				customer.customer_group = "Commercial"

			# Add contact details
			if self.primary_email:
				customer.email_id = self.primary_email

			if self.primary_phone:
				customer.mobile_no = self.primary_phone

			# Add tax ID if available
			if self.tax_id:
				customer.tax_id = self.tax_id

			customer.insert(ignore_permissions=True)

			# Link customer to tenant
			self.customer = customer.name
			self.save()

			frappe.msgprint(frappe._("Customer {0} created for tenant {1}").format(customer.name, self.tenant_name))
		except Exception as e:
			frappe.log_error(f"Failed to create customer for {self.name}: {str(e)}")
			frappe.msgprint(frappe._("Could not create customer automatically. Please create manually."), indicator="orange")

	def update_statistics(self):
		"""Update statistics from related members and subscriptions"""
		# Count total members
		self.total_members = frappe.db.count("GRM Member", {
			"tenant": self.name
		})

		# Count active subscriptions
		self.active_subscriptions = frappe.db.count("GRM Subscription", {
			"tenant": self.name,
			"status": "Active"
		})

		# Calculate total revenue from paid invoices
		if self.customer:
			total_revenue = frappe.db.sql("""
				SELECT SUM(grand_total) as total
				FROM `tabSales Invoice`
				WHERE customer = %s
				AND docstatus = 1
				AND status = 'Paid'
			""", self.customer)

			self.total_revenue = flt(total_revenue[0][0]) if total_revenue and total_revenue[0][0] else 0

			# Calculate total outstanding from unpaid/partially paid invoices
			total_outstanding = frappe.db.sql("""
				SELECT SUM(outstanding_amount) as total
				FROM `tabSales Invoice`
				WHERE customer = %s
				AND docstatus = 1
				AND outstanding_amount > 0
			""", self.customer)

			self.total_outstanding = flt(total_outstanding[0][0]) if total_outstanding and total_outstanding[0][0] else 0
