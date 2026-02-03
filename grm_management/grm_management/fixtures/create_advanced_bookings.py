# -*- coding: utf-8 -*-
# Create bookings with various durations to showcase advanced calendar

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, add_days

def create_advanced_bookings():
	"""Create bookings with various durations (0.5h, 1h, 1.5h, 2h, 3h, etc.)"""

	print("\n=== Creating Advanced Bookings with Various Durations ===\n")

	# Get existing spaces and tenants
	spaces = frappe.get_all("GRM Space", limit=4, pluck="name")
	tenants = frappe.get_all("GRM Tenant", limit=3, pluck="name")

	if not spaces or not tenants:
		print("Error: No spaces or tenants found. Please create test data first.")
		return

	today = nowdate()

	# Create bookings with various durations
	bookings_data = [
		# 30 minutes (0.5h)
		{
			"space": spaces[0],
			"tenant": tenants[0],
			"booking_date": add_days(today, 1),
			"start_time": "09:00:00",
			"end_time": "09:30:00",
			"duration": "0.5h"
		},
		# 1 hour
		{
			"space": spaces[0],
			"tenant": tenants[1],
			"booking_date": add_days(today, 1),
			"start_time": "10:00:00",
			"end_time": "11:00:00",
			"duration": "1h"
		},
		# 1.5 hours
		{
			"space": spaces[1],
			"tenant": tenants[0],
			"booking_date": add_days(today, 1),
			"start_time": "09:00:00",
			"end_time": "10:30:00",
			"duration": "1.5h"
		},
		# 2 hours
		{
			"space": spaces[1],
			"tenant": tenants[1],
			"booking_date": add_days(today, 1),
			"start_time": "14:00:00",
			"end_time": "16:00:00",
			"duration": "2h"
		},
		# 2.5 hours
		{
			"space": spaces[2],
			"tenant": tenants[2] if len(tenants) > 2 else tenants[0],
			"booking_date": add_days(today, 1),
			"start_time": "11:00:00",
			"end_time": "13:30:00",
			"duration": "2.5h"
		},
		# 3 hours
		{
			"space": spaces[2],
			"tenant": tenants[0],
			"booking_date": add_days(today, 1),
			"start_time": "15:00:00",
			"end_time": "18:00:00",
			"duration": "3h"
		},
		# 4 hours - Long meeting
		{
			"space": spaces[3] if len(spaces) > 3 else spaces[0],
			"tenant": tenants[1],
			"booking_date": add_days(today, 2),
			"start_time": "09:00:00",
			"end_time": "13:00:00",
			"duration": "4h"
		},
		# Half day (4.5 hours)
		{
			"space": spaces[3] if len(spaces) > 3 else spaces[1],
			"tenant": tenants[2] if len(tenants) > 2 else tenants[0],
			"booking_date": add_days(today, 2),
			"start_time": "14:00:00",
			"end_time": "18:30:00",
			"duration": "4.5h"
		},
		# Multiple short bookings on same day
		{
			"space": spaces[0],
			"tenant": tenants[0],
			"booking_date": add_days(today, 3),
			"start_time": "09:00:00",
			"end_time": "10:00:00",
			"duration": "1h"
		},
		{
			"space": spaces[0],
			"tenant": tenants[1],
			"booking_date": add_days(today, 3),
			"start_time": "11:30:00",
			"end_time": "13:00:00",
			"duration": "1.5h"
		},
		{
			"space": spaces[0],
			"tenant": tenants[2] if len(tenants) > 2 else tenants[0],
			"booking_date": add_days(today, 3),
			"start_time": "15:00:00",
			"end_time": "16:30:00",
			"duration": "1.5h"
		}
	]

	bookings = []
	for data in bookings_data:
		try:
			space_doc = frappe.get_doc("GRM Space", data["space"])
			duration_label = data.pop("duration")

			booking = frappe.get_doc({
				"doctype": "GRM Booking",
				"space": data["space"],
				"tenant": data["tenant"],
				"booking_date": data["booking_date"],
				"start_time": data["start_time"],
				"end_time": data["end_time"],
				"booking_type": "Hourly",
				"status": "Confirmed",
				"expiry_date": add_days(data["booking_date"], 7),
				"hourly_rate": space_doc.hourly_rate
			})
			booking.insert(ignore_permissions=True)
			bookings.append(booking.name)

			tenant_name = frappe.db.get_value("GRM Tenant", data["tenant"], "tenant_name")
			space_name = space_doc.space_name
			print(f"   ✓ Created {duration_label} booking: {space_name} - {tenant_name} on {data['booking_date']} at {data['start_time'][:5]}")
		except Exception as e:
			print(f"   ✗ Failed to create booking: {str(e)}")

	frappe.db.commit()

	print(f"\n=== Created {len(bookings)} Advanced Bookings ===")
	print("\nBooking Durations Created:")
	print("  - 30 minutes (0.5h)")
	print("  - 1 hour")
	print("  - 1.5 hours")
	print("  - 2 hours")
	print("  - 2.5 hours")
	print("  - 3 hours")
	print("  - 4 hours")
	print("  - 4.5 hours")
	print("\nView them in the Space Calendar page!")
	print("Calendar now supports bookings spanning across multiple hours.\n")

if __name__ == "__main__":
	create_advanced_bookings()
