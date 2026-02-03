# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, now


class GRMSpace(Document):
	def validate(self):
		"""Validate space data"""
		self.validate_capacity()
		self.set_pricing()
		
	def before_save(self):
		"""Update last_updated"""
		self.last_updated = now()
		
	def validate_capacity(self):
		"""Ensure capacity is greater than 0"""
		if not self.capacity or self.capacity <= 0:
			frappe.throw(_("Capacity must be greater than 0"))
			
	def set_pricing(self):
		"""Set pricing from Space Type if not using custom pricing"""
		if not self.use_custom_pricing and self.space_type:
			try:
				space_type = frappe.get_doc("GRM Space Type", self.space_type)
				self.hourly_rate = space_type.hourly_rate or 0
				self.daily_rate = space_type.daily_rate or 0
				self.monthly_rate = space_type.monthly_rate or 0
				self.annual_rate = space_type.annual_rate or 0
			except Exception as e:
				frappe.log_error(f"Error fetching Space Type pricing: {str(e)}")
				
	@frappe.whitelist()
	def set_rented(self, member, subscription=None):
		"""Set space as rented by a member"""
		self.status = "Rented"
		self.current_member = member
		self.current_subscription = subscription
		
		if subscription:
			try:
				sub_doc = frappe.get_doc("GRM Subscription", subscription)
				self.occupancy_start = sub_doc.start_date
				self.occupancy_end = sub_doc.end_date
			except Exception as e:
				frappe.log_error(f"Error fetching subscription dates: {str(e)}")
				
		self.save()
		frappe.msgprint(_("Space {0} marked as Rented").format(self.space_name), indicator="green")
		
	@frappe.whitelist()
	def set_available(self):
		"""Clear space to Available status"""
		self.status = "Available"
		self.current_member = None
		self.current_subscription = None
		self.occupancy_start = None
		self.occupancy_end = None
		
		self.save()
		frappe.msgprint(_("Space {0} marked as Available").format(self.space_name), indicator="green")
		
	@frappe.whitelist()
	def set_maintenance(self):
		"""Set space as under maintenance"""
		self.status = "Under Maintenance"
		self.save()
		frappe.msgprint(_("Space {0} marked as Under Maintenance").format(self.space_name), indicator="red")
		
	@frappe.whitelist()
	def update_statistics(self):
		"""Update space statistics"""
		# Count bookings
		self.total_bookings = frappe.db.count("GRM Booking", {"space": self.name})
		
		# Calculate total revenue
		revenue = frappe.db.sql("""
			SELECT SUM(total_amount) as total
			FROM `tabGRM Booking`
			WHERE space = %s AND status IN ('Checked-out', 'Confirmed')
		""", (self.name,), as_dict=True)
		
		self.total_revenue = revenue[0].total if revenue and revenue[0].total else 0
		
		# Get last booking date
		last_booking = frappe.db.sql("""
			SELECT booking_date
			FROM `tabGRM Booking`
			WHERE space = %s
			ORDER BY booking_date DESC
			LIMIT 1
		""", (self.name,), as_dict=True)
		
		if last_booking:
			self.last_booking_date = last_booking[0].booking_date
			
		self.save()
		
		return {
			"total_bookings": self.total_bookings,
			"total_revenue": self.total_revenue,
			"last_booking_date": self.last_booking_date
		}
