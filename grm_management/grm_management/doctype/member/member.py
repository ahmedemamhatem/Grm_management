# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import re


class Member(Document):
	def validate(self):
		"""Validate member data before saving"""
		self._validate_email_format()
		self._validate_email_unique()
		self._validate_id_expiry()
		self._validate_mobile_format()

	def after_insert(self):
		"""Auto-create Customer and generate ZK User ID after member creation"""
		self.create_customer()
		self.generate_zk_user_id()
		self.save()

	def _validate_email_format(self):
		"""Validate email format"""
		if self.primary_email:
			email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
			if not re.match(email_pattern, self.primary_email):
				frappe.throw(_("Invalid email format: {0}").format(self.primary_email))

	def _validate_email_unique(self):
		"""Ensure email is unique across all members"""
		if self.primary_email:
			existing = frappe.db.exists("Member", {
				"primary_email": self.primary_email,
				"name": ("!=", self.name)
			})
			if existing:
				frappe.throw(_("Email {0} is already registered with another member").format(self.primary_email))

	def _validate_id_expiry(self):
		"""Validate ID expiry is in the future"""
		if self.id_expiry:
			if frappe.utils.getdate(self.id_expiry) < frappe.utils.getdate(frappe.utils.nowdate()):
				frappe.msgprint(_("Warning: ID has already expired"), indicator="orange", alert=True)

	def _validate_mobile_format(self):
		"""Validate mobile number format (basic validation)"""
		if self.primary_mobile:
			# Remove spaces, dashes, parentheses
			mobile = re.sub(r'[\s\-\(\)]', '', self.primary_mobile)
			# Check if it contains only digits and optional + prefix
			if not re.match(r'^\+?\d{10,15}$', mobile):
				frappe.throw(_("Invalid mobile number format: {0}").format(self.primary_mobile))

	def create_customer(self):
		"""Create ERPNext Customer linked to this member"""
		if self.customer:
			# Customer already exists
			return

		try:
			customer = frappe.new_doc("Customer")
			customer.customer_name = self.member_name
			customer.customer_type = "Company" if self.member_type == "Company" else "Individual"
			customer.customer_group = "Commercial" if self.member_type == "Company" else "Individual"
			customer.territory = "All Territories"  # Default territory

			# Set contact details
			if self.primary_email:
				customer.email_id = self.primary_email
			if self.primary_mobile:
				customer.mobile_no = self.primary_mobile

			# Set payment terms if available
			if self.payment_terms:
				customer.payment_terms = self.payment_terms

			# Set credit limit if available
			if self.credit_limit:
				customer.credit_limits = []
				customer.append("credit_limits", {
					"credit_limit": self.credit_limit,
					"company": frappe.defaults.get_user_default("Company") or frappe.get_all("Company", limit=1)[0].name
				})

			customer.insert(ignore_permissions=True)

			# Link customer to member
			self.customer = customer.name
			frappe.msgprint(_("Customer {0} created successfully").format(customer.name), indicator="green", alert=True)

		except Exception as e:
			frappe.log_error(f"Error creating customer for member {self.name}: {str(e)}", "Member Customer Creation Error")
			frappe.throw(_("Error creating customer: {0}").format(str(e)))

	def generate_zk_user_id(self):
		"""Generate unique ZK User ID for access control"""
		if self.zk_user_id:
			# Already has ZK User ID
			return

		try:
			# Get the maximum existing ZK User ID
			max_id = frappe.db.sql("""
				SELECT MAX(CAST(zk_user_id AS UNSIGNED)) as max_id
				FROM `tabMember`
				WHERE zk_user_id IS NOT NULL AND zk_user_id != ''
			""", as_dict=True)

			if max_id and max_id[0].max_id:
				next_id = int(max_id[0].max_id) + 1
			else:
				# Start from 1001 if no existing IDs
				next_id = 1001

			self.zk_user_id = str(next_id)
			frappe.msgprint(_("ZK User ID {0} assigned").format(self.zk_user_id), indicator="green", alert=True)

		except Exception as e:
			frappe.log_error(f"Error generating ZK User ID for member {self.name}: {str(e)}", "ZK User ID Generation Error")
			# Don't throw error, just log it - ZK ID is not critical for member creation

	@frappe.whitelist()
	def update_statistics(self):
		"""Update member statistics - contracts, memberships, bookings, revenue"""
		# Count active contracts
		self.active_contracts = frappe.db.count("GRM Contract", {
			"member": self.name,
			"status": "Active"
		})

		# Count active memberships
		self.active_memberships = frappe.db.count("Membership", {
			"member": self.name,
			"status": "Active"
		})

		# Count total bookings
		self.total_bookings = frappe.db.count("Booking", {
			"member": self.name
		})

		# Calculate total revenue from paid Sales Invoices
		revenue = frappe.db.sql("""
			SELECT SUM(grand_total) as total
			FROM `tabSales Invoice`
			WHERE customer = %s AND docstatus = 1 AND status = 'Paid'
		""", (self.customer,), as_dict=True)

		self.total_revenue = revenue[0].total if revenue and revenue[0].total else 0

		# Calculate outstanding balance from unpaid/partially paid Sales Invoices
		outstanding = frappe.db.sql("""
			SELECT SUM(outstanding_amount) as total
			FROM `tabSales Invoice`
			WHERE customer = %s AND docstatus = 1 AND outstanding_amount > 0
		""", (self.customer,), as_dict=True)

		self.outstanding_balance = outstanding[0].total if outstanding and outstanding[0].total else 0

		# Get last visit date from Access Log
		last_visit = frappe.db.sql("""
			SELECT MAX(event_time) as last_visit
			FROM `tabAccess Log`
			WHERE member = %s AND event_type = 'Check-In'
		""", (self.name,), as_dict=True)

		if last_visit and last_visit[0].last_visit:
			self.last_visit_date = frappe.utils.getdate(last_visit[0].last_visit)

		self.save()
		frappe.msgprint(_("Statistics updated successfully"), indicator="green", alert=True)

		return {
			"active_contracts": self.active_contracts,
			"active_memberships": self.active_memberships,
			"total_bookings": self.total_bookings,
			"total_revenue": self.total_revenue,
			"outstanding_balance": self.outstanding_balance
		}
