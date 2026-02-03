# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, get_datetime_str, date_diff, getdate, nowdate


class GRMProperty(Document):
	def validate(self):
		"""Validate property data before saving"""
		self.validate_dates()
		self.calculate_financials()
		
	def before_save(self):
		"""Update statistics and financials before saving"""
		self.update_statistics()
		self.last_updated = get_datetime_str(frappe.utils.now())
		
	def validate_dates(self):
		"""Validate lease dates"""
		if self.lease_start_date and self.lease_end_date:
			if self.lease_end_date < self.lease_start_date:
				frappe.throw(_("Lease End Date must be after Start Date"))

			# Calculate lease duration in years
			days_diff = date_diff(self.lease_end_date, self.lease_start_date)
			self.lease_duration_years = flt(days_diff / 365.0, 2)
		
	def calculate_financials(self):
		"""Calculate all financial fields"""
		# Calculate annual rent
		self.annual_rent = flt(self.monthly_rent) * 12
		
		# Calculate total setup cost
		self.total_setup_cost = (
			flt(self.renovation_cost) +
			flt(self.furniture_cost) +
			flt(self.equipment_cost) +
			flt(self.other_setup_costs)
		)
		
		# Calculate monthly expenses
		total_monthly_expenses = sum([flt(e.amount) for e in self.expenses or []])
		
		# Calculate total monthly cost (rent + expenses)
		# Amortize setup costs over lease duration
		if flt(self.lease_duration_years) > 0:
			monthly_amortized_setup = flt(self.total_setup_cost) / (flt(self.lease_duration_years) * 12)
		else:
			monthly_amortized_setup = 0
			
		self.total_monthly_cost = (
			flt(self.monthly_rent) +
			total_monthly_expenses +
			monthly_amortized_setup
		)
		
		# Calculate expected monthly revenue (sum of space monthly rates)
		self.expected_monthly_revenue = sum([flt(s.monthly_rate) for s in self.spaces or []])
		
		# Calculate profit margin
		self.profit_margin = flt(self.actual_monthly_revenue) - flt(self.total_monthly_cost)
		
		# Calculate ROI percentage
		if self.total_monthly_cost > 0:
			self.roi_percentage = (flt(self.profit_margin) / flt(self.total_monthly_cost)) * 100
		else:
			self.roi_percentage = 0
			
	@frappe.whitelist()
	def update_statistics(self):
		"""Update property statistics"""
		# Count spaces
		space_count = len(self.spaces or [])
		
		# Get actual revenue from active subscriptions
		active_subscriptions = frappe.db.sql("""
			SELECT SUM(ss.monthly_rate) as total
			FROM `tabSubscription Space` ss
			JOIN `tabGRM Subscription` s ON s.name = ss.parent
			JOIN `tabGRM Space` sp ON sp.name = ss.space
			WHERE sp.property = %s
			AND s.status = 'Active'
		""", (self.name,), as_dict=True)
		
		if active_subscriptions and active_subscriptions[0].total:
			self.actual_monthly_revenue = flt(active_subscriptions[0].total)
		else:
			self.actual_monthly_revenue = 0
			
		# Recalculate financials
		self.calculate_financials()
		
		return {
			"total_spaces": space_count,
			"actual_monthly_revenue": self.actual_monthly_revenue,
			"profit_margin": self.profit_margin,
			"roi_percentage": self.roi_percentage
		}
		
	@frappe.whitelist()
	def create_spaces(self):
		"""Create actual GRM Space records from child table"""
		created_spaces = []
		
		for space_row in self.spaces or []:
			if not space_row.space:  # Only create if not already created
				# Create new space
				space = frappe.new_doc("GRM Space")
				space.space_name = space_row.space_name
				space.space_code = space_row.space_code
				space.location = self.location
				space.property = self.name
				space.space_type = space_row.space_type
				space.floor_number = space_row.floor_number
				space.area_sqm = space_row.area_sqm
				space.capacity = space_row.capacity
				space.monthly_rate = space_row.monthly_rate
				space.status = "Not Ready"  # Default to Not Ready
				
				space.insert()
				
				# Update child table with link
				space_row.space = space.name
				
				created_spaces.append(space.name)
				
		self.save()
		
		frappe.msgprint(
			_("Created {0} spaces successfully").format(len(created_spaces)),
			indicator="green",
			alert=True
		)
		
		return created_spaces
