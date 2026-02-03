# -*- coding: utf-8 -*-
# Simplified test data for KSA - skips complex entities

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, add_days

def create_simple_test_data():
	"""Create simple test data focusing on essential entities"""

	print("\n=== Creating KSA Test Data (Simplified) ===\n")

	# 1. Locations
	print("1. Creating Locations...")
	locations = create_locations()

	# 2. Space Types
	print("2. Creating Space Types...")
	space_types = create_space_types()

	# 3. Spaces
	print("3. Creating Spaces...")
	spaces = create_spaces(locations, space_types)

	# 4. Tenants
	print("4. Creating Tenants...")
	tenants = create_tenants()

	# 5. Members
	print("5. Creating Members...")
	members = create_members(tenants)

	# 6. Bookings
	print("6. Creating Bookings...")
	bookings = create_bookings(spaces, tenants)

	frappe.db.commit()

	print("\n=== Test Data Creation Complete ===\n")
	print(f"Created:")
	print(f"  - {len(locations)} Locations")
	print(f"  - {len(space_types)} Space Types")
	print(f"  - {len(spaces)} Spaces")
	print(f"  - {len(tenants)} Tenants")
	print(f"  - {len(members)} Members")
	print(f"  - {len(bookings)} Bookings")
	print("\nYou can now access:")
	print("  - GRM Coworking Space workspace")
	print("  - Space Calendar for bookings")
	print("  - GRM Tenant, GRM Member, GRM Space lists\n")

def create_locations():
	"""Create KSA locations"""
	country = "Saudi Arabia"
	if not frappe.db.exists("Country", country):
		country = frappe.get_all("Country", limit=1, pluck="name")[0] if frappe.db.count("Country") > 0 else None

	locations_data = [
		{
			"location_name": "Riyadh Business District",
			"address_line_1": "King Fahd Road, Al Olaya",
			"city": "Riyadh",
			"country": country,
			"status": "Active",
			"operating_hours_24_7": 1
		},
		{
			"location_name": "Jeddah Tech Hub",
			"address_line_1": "Prince Mohammed Bin Abdulaziz St",
			"city": "Jeddah",
			"country": country,
			"status": "Active",
			"operating_hours_24_7": 1
		}
	]

	locations = []
	for data in locations_data:
		if not frappe.db.exists("GRM Location", data["location_name"]):
			loc = frappe.get_doc({"doctype": "GRM Location", **data})
			loc.insert(ignore_permissions=True)
			locations.append(loc.name)
			print(f"   Created: {loc.name}")
		else:
			existing = frappe.get_value("GRM Location", {"location_name": data["location_name"]}, "name")
			locations.append(existing)
			print(f"   Exists: {data['location_name']}")

	return locations

def create_space_types():
	"""Create space types"""
	types_data = [
		{"space_type_name": "Meeting Room | قاعة اجتماعات", "description": "Conference and meeting space"},
		{"space_type_name": "Private Office | مكتب خاص", "description": "Fully enclosed private office"},
		{"space_type_name": "Hot Desk | مكتب مرن", "description": "Flexible desk in open area"},
		{"space_type_name": "Event Hall | قاعة فعاليات", "description": "Large event and conference hall"}
	]

	space_types = []
	for data in types_data:
		if not frappe.db.exists("GRM Space Type", data["space_type_name"]):
			st = frappe.get_doc({
				"doctype": "GRM Space Type",
				**data
			})
			st.insert(ignore_permissions=True)
			space_types.append(st.name)
			print(f"   Created: {st.name}")
		else:
			space_types.append(data["space_type_name"])
			print(f"   Exists: {data['space_type_name']}")

	return space_types

def create_spaces(locations, space_types):
	"""Create spaces linked to locations"""
	if not locations:
		print("   Error: No locations provided. Cannot create spaces.")
		return []

	spaces_data = [
		{
			"space_name": "Meeting Room 101 | قاعة 101",
			"location": locations[0] if len(locations) > 0 else None,
			"space_type": space_types[0],
			"capacity": 8,
			"hourly_rate": 200,
			"daily_rate": 1500,
			"monthly_rate": 30000,
			"status": "Available",
			"allow_booking": 1
		},
		{
			"space_name": "Executive Office A | مكتب تنفيذي أ",
			"location": locations[0] if len(locations) > 0 else None,
			"space_type": space_types[1],
			"capacity": 4,
			"hourly_rate": 300,
			"daily_rate": 2000,
			"monthly_rate": 45000,
			"status": "Available",
			"allow_booking": 1
		},
		{
			"space_name": "Hot Desk Zone 1 | منطقة المكاتب المرنة 1",
			"location": locations[1] if len(locations) > 1 else None,
			"space_type": space_types[2],
			"capacity": 1,
			"hourly_rate": 80,
			"daily_rate": 500,
			"monthly_rate": 10000,
			"status": "Available",
			"allow_booking": 1
		},
		{
			"space_name": "Conference Hall | قاعة المؤتمرات",
			"location": locations[1] if len(locations) > 1 else None,
			"space_type": space_types[0],
			"capacity": 20,
			"hourly_rate": 500,
			"daily_rate": 3500,
			"monthly_rate": 70000,
			"status": "Available",
			"allow_booking": 1
		},
	]

	spaces = []
	for data in spaces_data:
		if not frappe.db.exists("GRM Space", data["space_name"]):
			space = frappe.get_doc({
				"doctype": "GRM Space",
				**data
			})
			space.insert(ignore_permissions=True)
			spaces.append(space.name)
			print(f"   Created: {space.name}")
		else:
			spaces.append(data["space_name"])
			print(f"   Exists: {data['space_name']}")

	return spaces

def create_tenants():
	"""Create KSA tenants with compliance data"""
	customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "All Customer Groups"
	territory = frappe.db.get_value("Territory", {"is_group": 0}, "name") or "All Territories"

	tenants_data = [
		{
			"tenant_name": "TechVision Saudi",
			"email": "contact@techvision.sa",
			"phone": "+966-50-1234567",
			"company_name": "شركة تك فيجن السعودية",
			"commercial_registration": "1010567890",
			"vat_registration_number": "300123456789003",
			"iban": "SA0380000000608010167519",
			"zatca_compliance": 1
		},
		{
			"tenant_name": "Digital Hub Est",
			"email": "info@digitalhub.sa",
			"phone": "+966-50-2345678",
			"company_name": "مؤسسة المركز الرقمي",
			"commercial_registration": "2051234567",
			"vat_registration_number": "310234567890003",
			"iban": "SA4420000001250012345678",
			"zatca_compliance": 1
		},
		{
			"tenant_name": "Innovation KSA",
			"email": "hello@innovation.sa",
			"phone": "+966-50-3456789",
			"company_name": "مركز الابتكار",
			"commercial_registration": "2053456789",
			"vat_registration_number": "311345678900003"
		}
	]

	tenants = []
	for data in tenants_data:
		if not frappe.db.exists("GRM Tenant", data["tenant_name"]):
			# Create Customer
			if not frappe.db.exists("Customer", data["tenant_name"]):
				customer = frappe.get_doc({
					"doctype": "Customer",
					"customer_name": data["tenant_name"],
					"customer_type": "Company",
					"customer_group": customer_group,
					"territory": territory
				})
				customer.insert(ignore_permissions=True)

			# Create Tenant
			tenant_doc = frappe.get_doc({
				"doctype": "GRM Tenant",
				"tenant_name": data["tenant_name"],
				"customer": data["tenant_name"],
				"primary_email": data.get("email"),
				"primary_phone": data.get("phone"),
				"status": "Active",
				"commercial_registration": data.get("commercial_registration"),
				"vat_registration_number": data.get("vat_registration_number"),
				"iban": data.get("iban"),
				"zatca_compliance": data.get("zatca_compliance", 0)
			})
			tenant_doc.insert(ignore_permissions=True)
			tenants.append(tenant_doc.name)
			print(f"   Created: {tenant_doc.name}")
		else:
			tenants.append(data["tenant_name"])
			print(f"   Exists: {data['tenant_name']}")

	return tenants

def create_members(tenants):
	"""Create members for tenants"""
	members_data = [
		{
			"member_code": "MEM-001",
			"full_name": "Ahmed AlSaudi | أحمد السعودي",
			"primary_email": "ahmed@techvision.sa",
			"primary_mobile": "+966-55-1111111",
			"tenant": tenants[0] if len(tenants) > 0 else None,
			"id_type": "Saudi ID | الهوية الوطنية",
			"id_number": "1012345678"
		},
		{
			"member_code": "MEM-002",
			"full_name": "Mohammed Ali | محمد علي",
			"primary_email": "mohammed@digitalhub.sa",
			"primary_mobile": "+966-55-2222222",
			"tenant": tenants[1] if len(tenants) > 1 else None,
			"id_type": "Iqama | الإقامة",
			"id_number": "2112345678"
		},
		{
			"member_code": "MEM-003",
			"full_name": "Fatima Hassan | فاطمة حسن",
			"primary_email": "fatima@innovation.sa",
			"primary_mobile": "+966-55-3333333",
			"tenant": tenants[2] if len(tenants) > 2 else None,
			"id_type": "Saudi ID | الهوية الوطنية",
			"id_number": "1023456789"
		}
	]

	members = []
	for data in members_data:
		if not frappe.db.exists("GRM Member", {"member_code": data["member_code"]}):
			member = frappe.get_doc({
				"doctype": "GRM Member",
				"member_type": "Individual",
				"status": "Active",
				**data
			})
			member.insert(ignore_permissions=True)
			members.append(member.name)
			print(f"   Created: {member.member_code}")
		else:
			members.append(data["member_code"])
			print(f"   Exists: {data['member_code']}")

	return members

def create_bookings(spaces, tenants):
	"""Create sample bookings"""
	today = nowdate()

	bookings_data = [
		{
			"space": spaces[0] if len(spaces) > 0 else None,
			"tenant": tenants[0] if len(tenants) > 0 else None,
			"booking_date": add_days(today, 2),
			"start_time": "09:00:00",
			"end_time": "12:00:00",
			"booking_type": "Hourly",
			"status": "Confirmed"
		},
		{
			"space": spaces[1] if len(spaces) > 1 else None,
			"tenant": tenants[1] if len(tenants) > 1 else None,
			"booking_date": add_days(today, 3),
			"start_time": "14:00:00",
			"end_time": "17:00:00",
			"booking_type": "Hourly",
			"status": "Confirmed"
		},
		{
			"space": spaces[3] if len(spaces) > 3 else None,
			"tenant": tenants[2] if len(tenants) > 2 else None,
			"booking_date": add_days(today, 5),
			"start_time": "10:00:00",
			"end_time": "16:00:00",
			"booking_type": "Daily",
			"status": "Confirmed"
		}
	]

	bookings = []
	for data in bookings_data:
		if data["space"] and data["tenant"]:
			space_doc = frappe.get_doc("GRM Space", data["space"])

			booking = frappe.get_doc({
				"doctype": "GRM Booking",
				"space": data["space"],
				"tenant": data["tenant"],
				"booking_date": data["booking_date"],
				"start_time": data["start_time"],
				"end_time": data["end_time"],
				"booking_type": data["booking_type"],
				"status": data["status"],
				"expiry_date": add_days(data["booking_date"], 7),
				"hourly_rate": space_doc.hourly_rate if data["booking_type"] == "Hourly" else space_doc.daily_rate
			})
			booking.insert(ignore_permissions=True)
			bookings.append(booking.name)
			print(f"   Created: {booking.name}")

	return bookings

if __name__ == "__main__":
	create_simple_test_data()
