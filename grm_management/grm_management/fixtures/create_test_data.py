# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, add_days, add_months, now_datetime, get_time

def create_test_data():
	"""Create comprehensive test data for GRM Coworking Space"""

	print("\n=== Creating Test Data for GRM Coworking Space ===\n")

	# 1. Create Locations
	print("1. Creating Locations...")
	locations = create_locations()

	# 2. Create Properties
	print("2. Creating Properties...")
	properties = create_properties(locations)

	# 3. Create Space Types
	print("3. Creating Space Types...")
	space_types = create_space_types()

	# 4. Create Spaces
	print("4. Creating Spaces...")
	spaces = create_spaces(locations, properties, space_types)

	# 5. Create Landlords
	print("5. Creating Landlords...")
	landlords = create_landlords()

	# 6. Create Tenants
	print("6. Creating Tenants...")
	tenants = create_tenants()

	# 7. Create Members
	print("7. Creating Members...")
	members = create_members(tenants)

	# 8. Create Subscription Packages
	print("8. Creating Subscription Packages...")
	packages = create_packages()

	# 9. Create Sales Tax Template
	print("9. Creating Sales Tax Template...")
	tax_template = create_tax_template()

	# 10. Create Bookings (various statuses)
	print("10. Creating Bookings...")
	bookings = create_bookings(spaces, tenants, tax_template)

	# 11. Create Subscriptions
	print("11. Creating Subscriptions...")
	subscriptions = create_subscriptions(tenants, packages, spaces, members)

	frappe.db.commit()

	print("\n=== Test Data Creation Complete ===\n")
	print(f"Created:")
	print(f"  - {len(locations)} Locations")
	print(f"  - {len(properties)} Properties")
	print(f"  - {len(space_types)} Space Types")
	print(f"  - {len(spaces)} Spaces")
	print(f"  - {len(landlords)} Landlords")
	print(f"  - {len(tenants)} Tenants")
	print(f"  - {len(members)} Members")
	print(f"  - {len(packages)} Packages")
	print(f"  - {len(bookings)} Bookings")
	print(f"  - {len(subscriptions)} Subscriptions")
	print("\nYou can now test the Space Calendar and booking workflows!\n")

def create_locations():
	"""Create test locations for KSA"""
	# Get Saudi Arabia as country (or fallback to first available)
	country = "Saudi Arabia"
	if not frappe.db.exists("Country", country):
		country = frappe.get_all("Country", limit=1, pluck="name")[0] if frappe.db.count("Country") > 0 else None

	locations_data = [
		{
			"location_name": "Riyadh Business District",
			"address_line_1": "King Fahd Road, Al Olaya District",
			"city": "Riyadh",
			"country": country,
			"status": "Active",
			"operating_hours_24_7": 1
		},
		{
			"location_name": "Jeddah Tech Hub",
			"address_line_1": "Prince Mohammed Bin Abdulaziz Street",
			"city": "Jeddah",
			"country": country,
			"status": "Active",
			"operating_hours_24_7": 1
		},
		{
			"location_name": "Khobar Innovation Center",
			"address_line_1": "King Saud Road, Al Khobar",
			"city": "Khobar",
			"country": country,
			"status": "Active",
			"operating_hours_24_7": 1
		}
	]

	locations = []
	for data in locations_data:
		if not frappe.db.exists("GRM Location", data["location_name"]):
			loc = frappe.get_doc({
				"doctype": "GRM Location",
				**data
			})
			loc.insert(ignore_permissions=True)
			locations.append(loc.name)
			print(f"   Created Location: {loc.name}")
		else:
			locations.append(data["location_name"])
			print(f"   Location exists: {data['location_name']}")

	return locations

def create_properties(locations):
	"""Create test properties"""
	properties_data = [
		{"property_name": "Tech Tower A", "location": locations[0], "total_area": 5000},
		{"property_name": "Business Plaza B", "location": locations[1], "total_area": 3500},
		{"property_name": "Marina Complex C", "location": locations[2], "total_area": 4200}
	]

	properties = []
	for data in properties_data:
		if not frappe.db.exists("GRM Property", data["property_name"]):
			prop = frappe.get_doc({
				"doctype": "GRM Property",
				"property_name": data["property_name"],
				"location": data["location"],
				"total_area": data["total_area"],
				"status": "Active"
			})
			prop.insert(ignore_permissions=True)
			properties.append(prop.name)
			print(f"   Created Property: {prop.name}")
		else:
			properties.append(data["property_name"])
			print(f"   Property exists: {data['property_name']}")

	return properties

def create_space_types():
	"""Create test space types"""
	types_data = [
		{"space_type_name": "Private Office", "description": "Fully enclosed private office"},
		{"space_type_name": "Meeting Room", "description": "Conference and meeting space"},
		{"space_type_name": "Hot Desk", "description": "Flexible desk in open area"},
		{"space_type_name": "Dedicated Desk", "description": "Reserved desk in shared space"}
	]

	space_types = []
	for data in types_data:
		if not frappe.db.exists("GRM Space Type", data["space_type_name"]):
			st = frappe.get_doc({
				"doctype": "GRM Space Type",
				"space_type_name": data["space_type_name"],
				"description": data["description"]
			})
			st.insert(ignore_permissions=True)
			space_types.append(st.name)
			print(f"   Created Space Type: {st.name}")
		else:
			space_types.append(data["space_type_name"])
			print(f"   Space Type exists: {data['space_type_name']}")

	return space_types

def create_spaces(locations, properties, space_types):
	"""Create test spaces"""
	spaces_data = [
		# Meeting Rooms (bookable)
		{"space_name": "Meeting Room 101", "location": locations[0], "property": properties[0],
		 "space_type": space_types[1], "capacity": 8, "hourly_rate": 150, "daily_rate": 1000,
		 "status": "Available", "allow_booking": 1},
		{"space_name": "Meeting Room 102", "location": locations[0], "property": properties[0],
		 "space_type": space_types[1], "capacity": 6, "hourly_rate": 120, "daily_rate": 800,
		 "status": "Available", "allow_booking": 1},
		{"space_name": "Conference Hall A", "location": locations[1], "property": properties[1],
		 "space_type": space_types[1], "capacity": 20, "hourly_rate": 300, "daily_rate": 2000,
		 "status": "Available", "allow_booking": 1},

		# Private Offices (subscription-based, but bookable for trials)
		{"space_name": "Office 201", "location": locations[0], "property": properties[0],
		 "space_type": space_types[0], "capacity": 4, "hourly_rate": 200, "daily_rate": 1500,
		 "monthly_rate": 30000, "status": "Available", "allow_booking": 1},
		{"space_name": "Office 202", "location": locations[0], "property": properties[0],
		 "space_type": space_types[0], "capacity": 2, "hourly_rate": 150, "daily_rate": 1200,
		 "monthly_rate": 25000, "status": "Available", "allow_booking": 1},

		# Hot Desks (bookable)
		{"space_name": "Hot Desk Zone A", "location": locations[2], "property": properties[2],
		 "space_type": space_types[2], "capacity": 1, "hourly_rate": 50, "daily_rate": 300,
		 "status": "Available", "allow_booking": 1},
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
			print(f"   Created Space: {space.name}")
		else:
			spaces.append(data["space_name"])
			print(f"   Space exists: {data['space_name']}")

	return spaces

def create_landlords():
	"""Create test landlords"""
	landlords_data = [
		{"landlord_name": "Dubai Properties LLC", "email": "contact@dubaiproperties.ae", "phone": "+971-4-1234567"},
		{"landlord_name": "Marina Real Estate", "email": "info@marinagroup.ae", "phone": "+971-4-7654321"}
	]

	landlords = []
	for data in landlords_data:
		if not frappe.db.exists("GRM Landlord", data["landlord_name"]):
			landlord = frappe.get_doc({
				"doctype": "GRM Landlord",
				**data
			})
			landlord.insert(ignore_permissions=True)
			landlords.append(landlord.name)
			print(f"   Created Landlord: {landlord.name}")
		else:
			landlords.append(data["landlord_name"])
			print(f"   Landlord exists: {data['landlord_name']}")

	return landlords

def create_tenants():
	"""Create test tenants with KSA compliance data"""
	# Get default customer group and territory
	customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "All Customer Groups"
	territory = frappe.db.get_value("Territory", {"is_group": 0}, "name") or "All Territories"

	tenants_data = [
		{
			"tenant_name": "TechVision Saudi Co",
			"email": "contact@techvision.sa",
			"phone": "+966-50-1234567",
			"company_name": "شركة تك فيجن السعودية",
			"status": "Active",
			"commercial_registration": "1010567890",
			"vat_registration_number": "300123456789003",
			"iban": "SA0380000000608010167519",
			"bank_name": "Al Rajhi Bank",
			"zatca_compliance": 1,
			"muqeem_qiwa_registered": 1,
			"unified_number_700": "700567890"
		},
		{
			"tenant_name": "Digital Consulting Est",
			"email": "info@digitalconsult.sa",
			"phone": "+966-50-2345678",
			"company_name": "مؤسسة الاستشارات الرقمية",
			"status": "Active",
			"commercial_registration": "2051234567",
			"vat_registration_number": "310234567890003",
			"iban": "SA4420000001250012345678",
			"bank_name": "Saudi National Bank",
			"zatca_compliance": 1,
			"muqeem_qiwa_registered": 1
		},
		{
			"tenant_name": "Innovation Hub KSA",
			"email": "hello@innovationhub.sa",
			"phone": "+966-50-3456789",
			"company_name": "مركز الابتكار السعودي",
			"status": "Active",
			"commercial_registration": "2053456789",
			"vat_registration_number": "311345678900003",
			"iban": "SA1280000000123456789012",
			"bank_name": "Riyad Bank",
			"zatca_compliance": 1
		},
		{
			"tenant_name": "StartUp Valley LLC",
			"email": "team@startupvalley.sa",
			"phone": "+966-50-4567890",
			"company_name": "وادي الشركات الناشئة",
			"status": "Active",
			"commercial_registration": "1010678901",
			"vat_registration_number": "300456789012003",
			"iban": "SA6210000001234567890123",
			"bank_name": "Alinma Bank"
		}
	]

	tenants = []
	for data in tenants_data:
		if not frappe.db.exists("GRM Tenant", data["tenant_name"]):
			# Create Customer first
			if not frappe.db.exists("Customer", data["tenant_name"]):
				customer = frappe.get_doc({
					"doctype": "Customer",
					"customer_name": data["tenant_name"],
					"customer_type": "Company",
					"customer_group": customer_group,
					"territory": territory
				})
				customer.insert(ignore_permissions=True)

			# Create Tenant with KSA compliance fields
			tenant_data = {
				"doctype": "GRM Tenant",
				"tenant_name": data["tenant_name"],
				"customer": data["tenant_name"],
				"primary_email": data.get("email"),
				"primary_phone": data.get("phone"),
				"status": data["status"]
			}

			# Add optional KSA fields if present
			ksa_fields = [
				"commercial_registration", "cr_expiry_date", "iban", "bank_name",
				"vat_registration_number", "zatca_compliance", "muqeem_qiwa_registered",
				"unified_number_700", "industry", "company_size", "company_name"
			]
			for field in ksa_fields:
				if field in data:
					tenant_data[field] = data[field]

			tenant = frappe.get_doc(tenant_data)
			tenant.insert(ignore_permissions=True)
			tenants.append(tenant.name)
			print(f"   Created Tenant: {tenant.name}")
		else:
			tenants.append(data["tenant_name"])
			print(f"   Tenant exists: {data['tenant_name']}")

	return tenants

def create_members(tenants):
	"""Create test members linked to tenants"""
	members_data = [
		# TechStart Innovations members
		{"full_name": "Ahmed Hassan", "email": "ahmed@techstart.com", "phone": "+971-55-1111111",
		 "tenant": tenants[0], "member_type": "Primary", "status": "Active"},
		{"full_name": "Sarah Ahmed", "email": "sarah@techstart.com", "phone": "+971-55-2222222",
		 "tenant": tenants[0], "member_type": "Regular", "status": "Active"},

		# Digital Solutions Hub members
		{"full_name": "Mohammed Ali", "email": "mohammed@digitalhub.com", "phone": "+971-55-3333333",
		 "tenant": tenants[1], "member_type": "Primary", "status": "Active"},
		{"full_name": "Fatima Khan", "email": "fatima@digitalhub.com", "phone": "+971-55-4444444",
		 "tenant": tenants[1], "member_type": "Regular", "status": "Active"},

		# Creative Agency Co members
		{"full_name": "Omar Abdullah", "email": "omar@creativeagency.com", "phone": "+971-55-5555555",
		 "tenant": tenants[2], "member_type": "Primary", "status": "Active"},

		# StartUp Ventures members
		{"full_name": "Layla Ibrahim", "email": "layla@startupventures.com", "phone": "+971-55-6666666",
		 "tenant": tenants[3], "member_type": "Primary", "status": "Active"}
	]

	members = []
	for data in members_data:
		if not frappe.db.exists("GRM Member", {"email": data["email"]}):
			member = frappe.get_doc({
				"doctype": "GRM Member",
				**data
			})
			member.insert(ignore_permissions=True)
			members.append(member.name)
			print(f"   Created Member: {member.full_name}")
		else:
			existing = frappe.get_value("GRM Member", {"email": data["email"]}, "name")
			members.append(existing)
			print(f"   Member exists: {data['full_name']}")

	return members

def create_packages():
	"""Create subscription packages"""
	packages_data = [
		{"package_name": "Basic Flex", "package_type": "Hot Desk", "duration_months": 1,
		 "monthly_price": 1500, "description": "Flexible hot desk access"},
		{"package_name": "Professional Desk", "package_type": "Dedicated Desk", "duration_months": 3,
		 "monthly_price": 2500, "description": "Dedicated desk for 3 months"},
		{"package_name": "Private Office Standard", "package_type": "Private Office", "duration_months": 6,
		 "monthly_price": 8000, "description": "Private office for small team"},
		{"package_name": "Enterprise Office", "package_type": "Private Office", "duration_months": 12,
		 "monthly_price": 15000, "description": "Large private office annual plan"}
	]

	packages = []
	for data in packages_data:
		if not frappe.db.exists("GRM Subscription Package", data["package_name"]):
			package = frappe.get_doc({
				"doctype": "GRM Subscription Package",
				**data
			})
			package.insert(ignore_permissions=True)
			packages.append(package.name)
			print(f"   Created Package: {package.name}")
		else:
			packages.append(data["package_name"])
			print(f"   Package exists: {data['package_name']}")

	return packages

def create_tax_template():
	"""Create sales tax template (VAT 15% for KSA)"""
	template_name = "KSA VAT 15%"

	if not frappe.db.exists("Sales Taxes and Charges Template", template_name):
		try:
			company = frappe.defaults.get_user_default("Company") or frappe.get_all("Company", limit=1)[0].name

			# Find or create a tax account
			tax_account = frappe.db.get_value("Account", {
				"account_type": "Tax",
				"company": company,
				"is_group": 0
			}, "name")

			if not tax_account:
				# Skip tax template if no tax account exists
				print(f"   Skipped Tax Template (no tax account available)")
				return None

			template = frappe.get_doc({
				"doctype": "Sales Taxes and Charges Template",
				"title": template_name,
				"company": company,
				"taxes": [
					{
						"charge_type": "On Net Total",
						"account_head": tax_account,
						"description": "KSA VAT @ 15%",
						"rate": 15
					}
				]
			})
			template.insert(ignore_permissions=True)
			print(f"   Created Tax Template: {template_name}")
			return template_name
		except Exception as e:
			print(f"   Skipped Tax Template: {str(e)}")
			return None
	else:
		print(f"   Tax Template exists: {template_name}")
		return template_name

def create_bookings(spaces, tenants, tax_template):
	"""Create test bookings with various statuses"""
	today = nowdate()

	bookings_data = [
		# Confirmed bookings (future)
		{"space": spaces[0], "tenant": tenants[0], "booking_date": add_days(today, 2),
		 "start_time": "09:00:00", "end_time": "12:00:00", "booking_type": "Hourly",
		 "status": "Confirmed", "expiry_days": 7},

		{"space": spaces[1], "tenant": tenants[1], "booking_date": add_days(today, 3),
		 "start_time": "14:00:00", "end_time": "17:00:00", "booking_type": "Hourly",
		 "status": "Confirmed", "expiry_days": 7},

		{"space": spaces[2], "tenant": tenants[2], "booking_date": add_days(today, 5),
		 "start_time": "10:00:00", "end_time": "16:00:00", "booking_type": "Daily",
		 "status": "Confirmed", "expiry_days": 10},

		# Today's booking (in progress)
		{"space": spaces[3], "tenant": tenants[0], "booking_date": today,
		 "start_time": "09:00:00", "end_time": "18:00:00", "booking_type": "Daily",
		 "status": "Checked-in", "expiry_days": 7},

		# Past booking (completed)
		{"space": spaces[0], "tenant": tenants[3], "booking_date": add_days(today, -2),
		 "start_time": "13:00:00", "end_time": "15:00:00", "booking_type": "Hourly",
		 "status": "Checked-out", "expiry_days": 7},

		# Expired booking (will be marked as No-show by scheduler)
		{"space": spaces[1], "tenant": tenants[2], "booking_date": add_days(today, -10),
		 "start_time": "10:00:00", "end_time": "12:00:00", "booking_type": "Hourly",
		 "status": "Confirmed", "expiry_days": 5, "set_expired": True},
	]

	bookings = []
	for data in bookings_data:
		space_doc = frappe.get_doc("GRM Space", data["space"])
		set_expired = data.pop("set_expired", False)
		expiry_days = data.pop("expiry_days", 7)

		booking_data = {
			"doctype": "GRM Booking",
			"space": data["space"],
			"tenant": data["tenant"],
			"booking_date": data["booking_date"],
			"start_time": data["start_time"],
			"end_time": data["end_time"],
			"booking_type": data["booking_type"],
			"status": data["status"],
			"expiry_date": add_days(data["booking_date"], expiry_days if not set_expired else -2),
			"hourly_rate": space_doc.hourly_rate if data["booking_type"] == "Hourly" else space_doc.daily_rate
		}

		if tax_template:
			booking_data["sales_taxes_and_charges_template"] = tax_template

		booking = frappe.get_doc(booking_data)
		booking.insert(ignore_permissions=True)
		bookings.append(booking.name)
		print(f"   Created Booking: {booking.name} - {data['status']}")

	return bookings

def create_subscriptions(tenants, packages, spaces, members):
	"""Create test subscriptions"""
	today = nowdate()

	subscriptions_data = [
		# Active subscription
		{"tenant": tenants[0], "package": packages[2], "subscription_type": "Fixed Term",
		 "start_date": add_days(today, -30), "end_date": add_months(today, 5),
		 "status": "Active", "spaces": [
			 {"space": spaces[3], "member": members[0], "start_date": add_days(today, -30), "end_date": add_months(today, 5), "monthly_rate": 8000}
		 ]},

		# Recently started subscription
		{"tenant": tenants[1], "package": packages[1], "subscription_type": "Fixed Term",
		 "start_date": today, "end_date": add_months(today, 3),
		 "status": "Active", "spaces": [
			 {"space": spaces[4], "member": members[2], "start_date": today, "end_date": add_months(today, 3), "monthly_rate": 2500}
		 ]},
	]

	subscriptions = []
	for data in subscriptions_data:
		subscription = frappe.get_doc({
			"doctype": "GRM Subscription",
			"tenant": data["tenant"],
			"package": data["package"],
			"subscription_type": data["subscription_type"],
			"start_date": data["start_date"],
			"end_date": data["end_date"],
			"status": data["status"]
		})

		for space_data in data["spaces"]:
			subscription.append("spaces", space_data)

		subscription.insert(ignore_permissions=True)
		subscriptions.append(subscription.name)
		print(f"   Created Subscription: {subscription.name}")

	return subscriptions

# Main execution
if __name__ == "__main__":
	create_test_data()
