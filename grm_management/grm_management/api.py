# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, now_datetime, getdate, parse_time
from datetime import datetime, time


@frappe.whitelist()
def check_space_availability(space, date, start_time, end_time):
	"""Check if a space is available for booking

	Args:
		space: Space name
		date: Booking date
		start_time: Start time (HH:MM or HH:MM:SS)
		end_time: End time (HH:MM or HH:MM:SS)

	Returns:
		dict: {"available": bool, "reason": str}
	"""
	try:
		# Check if space exists and is Available
		space_doc = frappe.get_doc("Space", space)

		if space_doc.status not in ["Available"]:
			return {
				"available": False,
				"reason": f"Space is currently {space_doc.status}"
			}

		# Check for conflicting bookings
		conflicting_bookings = frappe.db.sql("""
			SELECT name, start_time, end_time
			FROM `tabBooking`
			WHERE space = %s
			AND booking_date = %s
			AND status IN ('Confirmed', 'Checked-In')
			AND (
				(start_time < %s AND end_time > %s)
				OR (start_time >= %s AND start_time < %s)
			)
		""", (space, date, end_time, start_time, start_time, end_time), as_dict=True)

		if conflicting_bookings:
			return {
				"available": False,
				"reason": f"Space is already booked during this time. Conflicting booking: {conflicting_bookings[0].name}"
			}

		return {
			"available": True,
			"reason": "Space is available"
		}

	except Exception as e:
		frappe.log_error(f"Error checking space availability: {str(e)}", "API Error")
		return {
			"available": False,
			"reason": f"Error: {str(e)}"
		}


@frappe.whitelist()
def get_member_access_status(member):
	"""Get comprehensive access status for a member

	Args:
		member: Member name

	Returns:
		dict: Access status information
	"""
	try:
		member_doc = frappe.get_doc("Member", member)

		# Get active contracts
		contracts = frappe.get_all("GRM Contract", filters={
			"member": member,
			"status": "Active"
		}, fields=["name", "contract_number", "start_date", "end_date", "net_monthly_rent"])

		# Get active memberships
		memberships = frappe.get_all("Membership", filters={
			"member": member,
			"status": "Active"
		}, fields=["name", "membership_number", "package", "start_date", "end_date", "access_type", "access_remaining"])

		# Get today's bookings
		todays_bookings = frappe.get_all("Booking", filters={
			"member": member,
			"booking_date": nowdate(),
			"status": ["in", ["Confirmed", "Checked-In"]]
		}, fields=["name", "space", "start_time", "end_time", "status"])

		# Check if member has any active access
		has_access = len(contracts) > 0 or len(memberships) > 0 or len(todays_bookings) > 0

		return {
			"member_name": member_doc.member_name,
			"member_code": member_doc.member_code,
			"status": member_doc.status,
			"has_access": has_access,
			"active_contracts": contracts,
			"active_memberships": memberships,
			"todays_bookings": todays_bookings,
			"last_visit_date": member_doc.last_visit_date
		}

	except Exception as e:
		frappe.log_error(f"Error getting member access status: {str(e)}", "API Error")
		frappe.throw(_("Error retrieving member access status: {0}").format(str(e)))


@frappe.whitelist()
def quick_check_in(member, location=None):
	"""Manual check-in for walk-in members

	Args:
		member: Member name
		location: Location name (optional)

	Returns:
		dict: Check-in status
	"""
	try:
		member_doc = frappe.get_doc("Member", member)

		# Verify member has active access (contract or membership)
		has_contract = frappe.db.count("GRM Contract", {
			"member": member,
			"status": "Active"
		}) > 0

		has_membership = frappe.db.count("Membership", {
			"member": member,
			"status": "Active"
		}) > 0

		if not has_contract and not has_membership:
			return {
				"success": False,
				"message": "Member has no active contract or membership"
			}

		# Create Access Log
		log = frappe.new_doc("Access Log")
		log.member = member
		log.zk_user_id = member_doc.zk_user_id
		log.event_type = "Check-In"
		log.event_time = now_datetime()
		log.context_type = "Manual"

		if location:
			log.location = location

		log.insert(ignore_permissions=True)

		# Update member last visit
		member_doc.last_visit_date = nowdate()
		member_doc.save()

		return {
			"success": True,
			"message": f"Check-in recorded for {member_doc.member_name}",
			"log_name": log.name,
			"time": log.event_time
		}

	except Exception as e:
		frappe.log_error(f"Error in quick check-in: {str(e)}", "API Error")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}


@frappe.whitelist()
def get_location_dashboard(location):
	"""Get dashboard data for a location

	Args:
		location: Location name

	Returns:
		dict: Dashboard statistics and information
	"""
	try:
		# Get space statistics
		total_spaces = frappe.db.count("Space", {"location": location})
		available_spaces = frappe.db.count("Space", {"location": location, "status": "Available"})
		occupied_spaces = frappe.db.count("Space", {"location": location, "status": "Occupied"})
		reserved_spaces = frappe.db.count("Space", {"location": location, "status": "Reserved"})

		occupancy_rate = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0

		# Get today's bookings
		todays_bookings = frappe.get_all("Booking", filters={
			"location": location,
			"booking_date": nowdate()
		}, fields=["name", "member", "space", "start_time", "end_time", "status"])

		# Get today's check-ins
		todays_checkins = frappe.db.sql("""
			SELECT member, event_time, context_type, context_name
			FROM `tabAccess Log`
			WHERE location = %s
			AND DATE(event_time) = %s
			AND event_type = 'Check-In'
			ORDER BY event_time DESC
			LIMIT 20
		""", (location, nowdate()), as_dict=True)

		# Get active contracts for this location
		active_contracts = frappe.db.sql("""
			SELECT DISTINCT c.name, c.contract_number, c.member, c.start_date, c.end_date
			FROM `tabGRM Contract` c
			JOIN `tabContract Space` cs ON cs.parent = c.name
			JOIN `tabSpace` s ON s.name = cs.space
			WHERE s.location = %s
			AND c.status = 'Active'
		""", (location,), as_dict=True)

		return {
			"location": location,
			"total_spaces": total_spaces,
			"available_spaces": available_spaces,
			"occupied_spaces": occupied_spaces,
			"reserved_spaces": reserved_spaces,
			"occupancy_rate": round(occupancy_rate, 2),
			"todays_bookings": todays_bookings,
			"todays_checkins": todays_checkins,
			"active_contracts": len(active_contracts)
		}

	except Exception as e:
		frappe.log_error(f"Error getting location dashboard: {str(e)}", "API Error")
		frappe.throw(_("Error retrieving location dashboard: {0}").format(str(e)))


@frappe.whitelist()
def get_available_spaces(location=None, date=None, start_time=None, end_time=None, space_type=None):
	"""Get list of available spaces based on filters

	Args:
		location: Location name (optional)
		date: Booking date (optional, defaults to today)
		start_time: Start time (optional)
		end_time: End time (optional)
		space_type: Space Type name (optional)

	Returns:
		list: Available spaces with details
	"""
	try:
		if not date:
			date = nowdate()

		# Build filters for spaces
		filters = {"status": "Available"}

		if location:
			filters["location"] = location

		if space_type:
			filters["space_type"] = space_type

		# Get all potentially available spaces
		spaces = frappe.get_all("Space", filters=filters, fields=[
			"name", "space_name", "space_code", "location", "space_type",
			"capacity", "hourly_rate", "daily_rate", "monthly_rate", "area_sqm"
		])

		# If time range specified, filter out spaces with conflicting bookings
		if start_time and end_time:
			available_spaces = []

			for space in spaces:
				result = check_space_availability(space.name, date, start_time, end_time)
				if result.get("available"):
					available_spaces.append(space)

			return available_spaces
		else:
			return spaces

	except Exception as e:
		frappe.log_error(f"Error getting available spaces: {str(e)}", "API Error")
		frappe.throw(_("Error retrieving available spaces: {0}").format(str(e)))


@frappe.whitelist()
def get_member_bookings(member, from_date=None, to_date=None, status=None):
	"""Get bookings for a member

	Args:
		member: Member name
		from_date: Start date filter (optional)
		to_date: End date filter (optional)
		status: Status filter (optional)

	Returns:
		list: Bookings
	"""
	try:
		filters = {"member": member}

		if from_date:
			filters["booking_date"] = [">=", from_date]

		if to_date:
			if "booking_date" in filters:
				filters["booking_date"] = ["between", [from_date, to_date]]
			else:
				filters["booking_date"] = ["<=", to_date]

		if status:
			filters["status"] = status

		bookings = frappe.get_all("Booking", filters=filters, fields=[
			"name", "space", "booking_date", "start_time", "end_time",
			"status", "rate_type", "total_amount", "actual_check_in", "actual_check_out"
		], order_by="booking_date desc")

		return bookings

	except Exception as e:
		frappe.log_error(f"Error getting member bookings: {str(e)}", "API Error")
		frappe.throw(_("Error retrieving member bookings: {0}").format(str(e)))


@frappe.whitelist()
def create_booking(member, space, booking_date, start_time, end_time, rate_type="Hourly Rate", membership=None):
	"""Quick API to create a booking

	Args:
		member: Member name
		space: Space name
		booking_date: Booking date
		start_time: Start time
		end_time: End time
		rate_type: Hourly Rate, Daily Rate, or Package
		membership: Membership name (required if rate_type is Package)

	Returns:
		dict: Booking details
	"""
	try:
		# Check availability
		availability = check_space_availability(space, booking_date, start_time, end_time)

		if not availability.get("available"):
			return {
				"success": False,
				"message": availability.get("reason")
			}

		# Create booking
		booking = frappe.new_doc("Booking")
		booking.member = member
		booking.space = space
		booking.booking_date = booking_date
		booking.start_time = start_time
		booking.end_time = end_time
		booking.rate_type = rate_type
		booking.status = "Draft"

		if rate_type == "Package" and membership:
			booking.membership = membership

		# Get space details for pricing
		space_doc = frappe.get_doc("Space", space)
		booking.hourly_rate = space_doc.hourly_rate
		booking.daily_rate = space_doc.daily_rate

		booking.insert(ignore_permissions=True)

		return {
			"success": True,
			"message": "Booking created successfully",
			"booking_name": booking.name,
			"total_amount": booking.total_amount
		}

	except Exception as e:
		frappe.log_error(f"Error creating booking: {str(e)}", "API Error")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}
