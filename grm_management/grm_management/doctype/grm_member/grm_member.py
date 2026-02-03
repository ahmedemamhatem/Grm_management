# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
import re


class GRMMember(Document):
	def validate(self):
		"""Validate member data"""
		self.validate_email()
		self.validate_mobile()
		
	def after_insert(self):
		"""Generate ZK User ID"""
		self.generate_zk_user_id()
		self.save()
		
	def validate_email(self):
		"""Validate email format"""
		if self.primary_email:
			if not frappe.utils.validate_email_address(self.primary_email):
				frappe.throw(_("Invalid email: {0}").format(self.primary_email))
				
	def validate_mobile(self):
		"""Validate mobile format"""
		if self.primary_mobile:
			mobile = re.sub(r'[\s\-\(\)]', '', self.primary_mobile)
			if not re.match(r'^\+?\d{10,15}$', mobile):
				frappe.throw(_("Invalid mobile: {0}").format(self.primary_mobile))
				
	def generate_zk_user_id(self):
		"""Generate ZK User ID"""
		if self.zk_user_id:
			return
			
		try:
			max_id = frappe.db.sql("""
				SELECT MAX(CAST(zk_user_id AS UNSIGNED)) as max_id
				FROM `tabGRM Member`
				WHERE zk_user_id IS NOT NULL AND zk_user_id != ''
			""", as_dict=True)
			
			if max_id and max_id[0].max_id:
				next_id = int(max_id[0].max_id) + 1
			else:
				next_id = 1001
				
			self.zk_user_id = str(next_id)
			
		except Exception as e:
			frappe.log_error(f"Error generating ZK User ID: {str(e)}")
			
	@frappe.whitelist()
	def update_statistics(self):
		"""Update member statistics"""
		self.total_subscriptions = frappe.db.count("GRM Subscription", {"member": self.name})
		self.active_subscriptions = frappe.db.count("GRM Subscription", {"member": self.name, "status": "Active"})
		self.total_bookings = frappe.db.count("GRM Booking", {"member": self.name})

		# Get statistics from tenant's customer if available
		if self.tenant:
			tenant_doc = frappe.get_doc("GRM Tenant", self.tenant)
			if tenant_doc.customer:
				revenue = frappe.db.sql("""
					SELECT SUM(grand_total) as total
					FROM `tabSales Invoice`
					WHERE customer = %s AND docstatus = 1 AND status = 'Paid'
				""", (tenant_doc.customer,), as_dict=True)
				self.total_revenue = revenue[0].total if revenue and revenue[0].total else 0

				outstanding = frappe.db.sql("""
					SELECT SUM(outstanding_amount) as total
					FROM `tabSales Invoice`
					WHERE customer = %s AND docstatus = 1 AND outstanding_amount > 0
				""", (tenant_doc.customer,), as_dict=True)
				self.outstanding_balance = outstanding[0].total if outstanding and outstanding[0].total else 0

		visits = frappe.db.sql("""
			SELECT COUNT(*) as total, MAX(event_time) as last_visit
			FROM `tabGRM Access Log`
			WHERE member = %s AND event_type = 'Check-in'
		""", (self.name,), as_dict=True)

		if visits:
			self.total_visits = visits[0].total or 0
			self.last_visit_date = visits[0].last_visit

		self.save()
		return {"total_subscriptions": self.total_subscriptions, "active_subscriptions": self.active_subscriptions, "total_revenue": self.total_revenue}
