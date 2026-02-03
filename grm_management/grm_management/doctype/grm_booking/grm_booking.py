# Copyright (c) 2026, Wael ELsafty and contributors
import frappe
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, now

class GRMBooking(Document):
	def validate(self):
		self.calculate_duration()
		self.calculate_pricing()
		
	def calculate_duration(self):
		if self.start_time and self.end_time:
			self.duration_hours = time_diff_in_hours(self.end_time, self.start_time)
			self.total_hours = self.duration_hours
			
	def calculate_pricing(self):
		if self.rate_type == "Hourly" and self.hourly_rate and self.total_hours:
			self.subtotal = flt(self.hourly_rate) * flt(self.total_hours)
		self.total_amount = flt(self.subtotal) - flt(self.discount) + flt(self.tax) + flt(self.overtime_charges)
		
	@frappe.whitelist()
	def check_in(self):
		self.actual_check_in = now()
		self.status = "Checked-in"
		self.save()
		frappe.msgprint("Checked in successfully", indicator="green")
		
	@frappe.whitelist()
	def check_out(self):
		self.actual_check_out = now()
		self.status = "Checked-out"
		if self.actual_check_in and self.actual_check_out:
			actual_hours = time_diff_in_hours(self.actual_check_out, self.actual_check_in)
			if actual_hours > self.total_hours:
				self.overtime_hours = actual_hours - self.total_hours
				self.overtime_charges = self.overtime_hours * flt(self.hourly_rate) * 1.5
		self.calculate_pricing()
		self.save()
		frappe.msgprint("Checked out successfully", indicator="green")
