# -*- coding: utf-8 -*-
# Complete Test Data Generator for GRM Management
# This creates comprehensive test data with ALL fields populated

import frappe
from frappe.utils import nowdate, add_days, add_months, now_datetime, get_datetime
import random


def run():
	"""Main function to create all test data"""
	print("\n" + "="*80)
	print("CREATING COMPLETE TEST DATA WITH ALL FIELDS")
	print("="*80 + "\n")

	try:
		# Step 1: Prerequisites
		create_prerequisites()

		# Step 2: Locations
		locations = create_grm_locations()

		# Step 3: Space Types
		space_types = create_space_types()

		# Step 4: Amenities
		amenities = create_amenities()

		# Step 5: Spaces
		spaces = create_spaces(locations, space_types, amenities)

		# Step 6: Members
		members = create_members()

		# Step 7: Packages (ERPNext)
		packages = create_packages(locations)

		# Step 8: Access Devices
		devices = create_access_devices(locations)

		# Step 9: Contracts
		contracts = create_contracts(members, spaces)

		# Step 10: Memberships
		memberships = create_memberships(members, packages)

		# Step 11: Bookings
		bookings = create_bookings(members, spaces)

		# Step 12: Location Expenses
		expenses = create_location_expenses(locations)

		# Step 13: BioTime Settings
		create_biotime_settings()

		print("\n" + "="*80)
		print("COMPLETE TEST DATA CREATION FINISHED!")
		print("="*80)

		print_summary(locations, space_types, spaces, members, contracts,
		              memberships, bookings, devices, expenses)

	except Exception as e:
		frappe.db.rollback()
		print(f"\n❌ ERROR: {str(e)}")
		import traceback
		traceback.print_exc()
		raise


def create_prerequisites():
	"""Create required ERPNext master data"""
	print("📋 Creating Prerequisites...")

	# Get or create root Customer Group
	root_cg = frappe.db.get_value("Customer Group", {"is_group": 1, "parent_customer_group": ["in", ["", None]]}, "name")

	if not root_cg:
		# Check if "All Customer Groups" exists but query failed
		if frappe.db.exists("Customer Group", "All Customer Groups"):
			root_cg = "All Customer Groups"
		else:
			# Create root Customer Group
			root = frappe.new_doc("Customer Group")
			root.customer_group_name = "All Customer Groups"
			root.is_group = 1
			root.parent_customer_group = ""
			root.insert(ignore_permissions=True)
			root_cg = "All Customer Groups"
			print("  ✓ Root Customer Group: All Customer Groups")

	# Create Customer Groups
	for group in ["Individual", "Commercial"]:
		if not frappe.db.exists("Customer Group", group):
			cg = frappe.new_doc("Customer Group")
			cg.customer_group_name = group
			cg.parent_customer_group = root_cg
			cg.is_group = 0
			cg.insert(ignore_permissions=True)
			print(f"  ✓ Customer Group: {group}")

	# Get or create root Territory
	root_territory = frappe.db.get_value("Territory", {"is_group": 1, "parent_territory": ["in", ["", None]]}, "name")

	if not root_territory:
		# Check if "All Territories" exists but query failed
		if frappe.db.exists("Territory", "All Territories"):
			root_territory = "All Territories"
		else:
			# Create root Territory
			root_terr = frappe.new_doc("Territory")
			root_terr.territory_name = "All Territories"
			root_terr.is_group = 1
			root_terr.parent_territory = ""
			root_terr.insert(ignore_permissions=True)
			print("  ✓ Root Territory: All Territories")

	# Get or create root Supplier Group
	root_sg = frappe.db.get_value("Supplier Group", {"is_group": 1, "parent_supplier_group": ["in", ["", None]]}, "name")

	if not root_sg:
		# Check if "All Supplier Groups" exists but query failed
		if frappe.db.exists("Supplier Group", "All Supplier Groups"):
			root_sg = "All Supplier Groups"
		else:
			# Create root Supplier Group
			root_s = frappe.new_doc("Supplier Group")
			root_s.supplier_group_name = "All Supplier Groups"
			root_s.is_group = 1
			root_s.parent_supplier_group = ""
			root_s.insert(ignore_permissions=True)
			root_sg = "All Supplier Groups"
			print("  ✓ Root Supplier Group: All Supplier Groups")

	# Create Supplier Group: Services
	if not frappe.db.exists("Supplier Group", "Services"):
		sg = frappe.new_doc("Supplier Group")
		sg.supplier_group_name = "Services"
		sg.parent_supplier_group = root_sg
		sg.is_group = 0
		sg.insert(ignore_permissions=True)
		print("  ✓ Supplier Group: Services")

	# Create Suppliers
	suppliers = [
		"Property Landlord Co.",
		"Power & Water Authority",
		"Internet Service Provider",
		"Cleaning Services Ltd.",
		"Maintenance & Repairs Inc.",
		"Security Services Co."
	]

	for supplier_name in suppliers:
		if not frappe.db.exists("Supplier", supplier_name):
			supplier = frappe.new_doc("Supplier")
			supplier.supplier_name = supplier_name
			supplier.supplier_group = "Services"
			supplier.supplier_type = "Company"
			supplier.insert(ignore_permissions=True)
			print(f"  ✓ Supplier: {supplier_name}")

	# Create Industry Types
	industries = [
		"Technology", "Finance", "Healthcare", "Education",
		"Consulting", "Marketing", "Legal Services", "Real Estate"
	]

	for industry_name in industries:
		if not frappe.db.exists("Industry Type", industry_name):
			industry = frappe.new_doc("Industry Type")
			industry.industry = industry_name
			industry.insert(ignore_permissions=True)
			print(f"  ✓ Industry: {industry_name}")

	frappe.db.commit()


def create_grm_locations():
	"""Create GRM Locations with ALL fields"""
	print("\n📍 Creating GRM Locations...")

	locations_data = [
		{
			"location_name": "Downtown Business Hub",
			"location_code": "DTH-001",
			"status": "Active",
			"email": "downtown@coworkspace.sa",
			"phone": "+966-11-2345678",
			"website": "https://downtown.coworkspace.sa",
			"address_line_1": "King Fahd Road, Tower A",
			"address_line_2": "Floor 15, Suite 1501",
			"city": "Riyadh",
			"state": "Riyadh Province",
			"postal_code": "11564",
			"country": "Saudi Arabia",
			"rent_cost": 80000,
			"utilities_cost": 12000,
			"maintenance_cost": 8000,
			"staff_cost": 35000,
			"other_costs": 5000
		},
		{
			"location_name": "Tech Park Innovation Center",
			"location_code": "TPI-001",
			"status": "Active",
			"email": "techpark@coworkspace.sa",
			"phone": "+966-11-9876543",
			"website": "https://techpark.coworkspace.sa",
			"address_line_1": "King Abdullah Financial District",
			"address_line_2": "Building 7, 3rd Floor",
			"city": "Riyadh",
			"state": "Riyadh Province",
			"postal_code": "13519",
			"country": "Saudi Arabia",
			"rent_cost": 100000,
			"utilities_cost": 15000,
			"maintenance_cost": 10000,
			"staff_cost": 45000,
			"other_costs": 8000
		},
		{
			"location_name": "Creative District Studio",
			"location_code": "CDS-001",
			"status": "Active",
			"email": "creative@coworkspace.sa",
			"phone": "+966-11-5554433",
			"website": "https://creative.coworkspace.sa",
			"address_line_1": "Olaya Street, Al Faisaliah Complex",
			"address_line_2": "Level 2, West Wing",
			"city": "Riyadh",
			"state": "Riyadh Province",
			"postal_code": "11495",
			"country": "Saudi Arabia",
			"rent_cost": 65000,
			"utilities_cost": 9000,
			"maintenance_cost": 6000,
			"staff_cost": 28000,
			"other_costs": 4000
		}
	]

	locations = []
	for loc_data in locations_data:
		if not frappe.db.exists("GRM Location", loc_data["location_code"]):
			location = frappe.new_doc("GRM Location")
			location.update(loc_data)

			# Add operating hours
			days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
			for day in days[:5]:  # Mon-Fri
				location.append("operating_hours", {
					"day": day,
					"opening_time": "08:00:00",
					"closing_time": "20:00:00"
				})
			for day in days[5:]:  # Sat-Sun
				location.append("operating_hours", {
					"day": day,
					"opening_time": "10:00:00",
					"closing_time": "18:00:00"
				})

			location.insert(ignore_permissions=True)
			locations.append(location.name)
			print(f"  ✓ Location: {location.location_name} ({location.location_code})")
			print(f"    - Total Monthly Costs: {location.total_monthly_costs:,.0f} SAR")
		else:
			# Location already exists, add to list
			locations.append(loc_data["location_code"])

	frappe.db.commit()
	return locations


def create_space_types():
	"""Create Space Types with ALL fields"""
	print("\n🏢 Creating Space Types...")

	types_data = [
		{
			"type_name": "Private Office",
			"type_code": "PO",
			"description": "Fully furnished private office with lockable door, ideal for teams of 2-6 people",
			"default_capacity": 4,
			"icon": "fa fa-building",
			"color": "#3498db",
			"allow_hourly": 0,
			"allow_daily": 1,
			"allow_monthly": 1,
			"allow_long_term": 1,
			"min_booking_hours": 8,
			"advance_booking_days": 30,
			"daily_rate": 600,
			"monthly_rate": 12000
		},
		{
			"type_name": "Hot Desk",
			"type_code": "HD",
			"description": "Flexible shared workspace, first-come first-served",
			"default_capacity": 1,
			"icon": "fa fa-laptop",
			"color": "#e74c3c",
			"allow_hourly": 1,
			"allow_daily": 1,
			"allow_monthly": 1,
			"allow_long_term": 0,
			"min_booking_hours": 2,
			"max_booking_hours": 10,
			"advance_booking_days": 7,
			"hourly_rate": 50,
			"daily_rate": 300,
			"monthly_rate": 5000
		},
		{
			"type_name": "Dedicated Desk",
			"type_code": "DD",
			"description": "Your own desk in a shared office environment",
			"default_capacity": 1,
			"icon": "fa fa-user-circle",
			"color": "#2ecc71",
			"allow_hourly": 0,
			"allow_daily": 0,
			"allow_monthly": 1,
			"allow_long_term": 1,
			"advance_booking_days": 14,
			"monthly_rate": 7000
		},
		{
			"type_name": "Meeting Room",
			"type_code": "MR",
			"description": "Professional meeting room with AV equipment",
			"default_capacity": 8,
			"icon": "fa fa-users",
			"color": "#f39c12",
			"allow_hourly": 1,
			"allow_daily": 1,
			"allow_monthly": 0,
			"allow_long_term": 0,
			"min_booking_hours": 1,
			"max_booking_hours": 8,
			"advance_booking_days": 14,
			"hourly_rate": 150,
			"daily_rate": 1000
		}
	]

	space_types = []
	for type_data in types_data:
		if not frappe.db.exists("Space Type", type_data["type_code"]):
			space_type = frappe.new_doc("Space Type")
			space_type.update(type_data)
			space_type.insert(ignore_permissions=True)
			space_types.append(space_type.name)
			print(f"  ✓ Space Type: {space_type.type_name} ({space_type.type_code})")
		else:
			# Space Type already exists, add to list
			space_types.append(type_data["type_code"])

	frappe.db.commit()
	return space_types


def create_amenities():
	"""Create Amenities"""
	print("\n✨ Creating Amenities...")

	amenities_data = [
		{"name": "High-Speed WiFi", "code": "WIFI", "category": "Technology", "icon": "fa fa-wifi"},
		{"name": "Printer/Scanner", "code": "PRINT", "category": "Technology", "icon": "fa fa-print"},
		{"name": "Whiteboard", "code": "WB", "category": "Furniture", "icon": "fa fa-chalkboard"},
		{"name": "TV/Monitor", "code": "TV", "category": "Technology", "icon": "fa fa-tv"},
		{"name": "Coffee/Tea", "code": "COFFEE", "category": "Service", "icon": "fa fa-coffee"},
		{"name": "Air Conditioning", "code": "AC", "category": "Facility", "icon": "fa fa-snowflake"},
		{"name": "Natural Light", "code": "LIGHT", "category": "Facility", "icon": "fa fa-sun"},
		{"name": "Standing Desk", "code": "SDESK", "category": "Furniture", "icon": "fa fa-desktop"},
		{"name": "Phone Booth", "code": "PHONE", "category": "Facility", "icon": "fa fa-phone"},
		{"name": "Kitchen Access", "code": "KITCHEN", "category": "Facility", "icon": "fa fa-utensils"},
		{"name": "Locker", "code": "LOCKER", "category": "Facility", "icon": "fa fa-lock"},
		{"name": "24/7 Access", "code": "247", "category": "Service", "icon": "fa fa-clock"}
	]

	amenities = []
	for am_data in amenities_data:
		existing = frappe.db.exists("Amenity", {"amenity_code": am_data["code"]})
		if not existing:
			amenity = frappe.new_doc("Amenity")
			amenity.amenity_name = am_data["name"]
			amenity.amenity_code = am_data["code"]
			amenity.category = am_data["category"]
			amenity.icon = am_data["icon"]
			amenity.is_chargeable = 0
			amenity.insert(ignore_permissions=True)
			amenities.append(amenity.name)
			print(f"  ✓ Amenity: {am_data['name']} ({am_data['code']})")
		else:
			# Amenity already exists, add to list
			amenities.append(existing)

	frappe.db.commit()
	return amenities


def create_spaces(locations, space_types, amenities):
	"""Create Spaces with ALL fields"""
	print("\n🚪 Creating Spaces...")

	spaces = []
	space_counter = 1

	for location in locations:
		loc_code = frappe.db.get_value("GRM Location", location, "location_code")

		# Private Offices (3 per location)
		for i in range(1, 4):
			space_code = f"{loc_code}-PO{i:02d}"
			if frappe.db.exists("Space", space_code):
				spaces.append(space_code)
				continue

			space = frappe.new_doc("Space")
			space.space_name = f"Private Office {loc_code}-PO{i:02d}"
			space.space_code = space_code
			space.location = location
			space.space_type = "PO"
			space.capacity = random.choice([2, 4, 6])
			space.area_sqm = random.randint(20, 40)
			space.floor = f"{random.randint(1, 5)}th Floor"
			space.status = "Available"
			space.description = f"Spacious private office with premium furnishings"
			space.use_custom_pricing = 0

			# Virtual tour URL
			space.virtual_tour_url = f"https://virtualtour.com/space/{space.space_code}"

			# Access control
			space.requires_fingerprint = 1
			space.requires_access_card = 0
			space.door_number = f"{i:02d}"

			space.insert(ignore_permissions=True)
			spaces.append(space.name)
			space_counter += 1

		# Hot Desks (5 per location)
		for i in range(1, 6):
			space_code = f"{loc_code}-HD{i:02d}"
			if frappe.db.exists("Space", space_code):
				spaces.append(space_code)
				continue

			space = frappe.new_doc("Space")
			space.space_name = f"Hot Desk {loc_code}-HD{i:02d}"
			space.space_code = space_code
			space.location = location
			space.space_type = "HD"
			space.capacity = 1
			space.area_sqm = 4
			space.floor = f"{random.randint(1, 3)}th Floor"
			space.status = "Available"
			space.use_custom_pricing = 0
			space.insert(ignore_permissions=True)
			spaces.append(space.name)
			space_counter += 1

		# Meeting Rooms (2 per location)
		for i in range(1, 3):
			space_code = f"{loc_code}-MR{i:02d}"
			if frappe.db.exists("Space", space_code):
				spaces.append(space_code)
				continue

			space = frappe.new_doc("Space")
			space.space_name = f"Meeting Room {loc_code}-MR{i:02d}"
			space.space_code = space_code
			space.location = location
			space.space_type = "MR"
			space.capacity = random.choice([6, 8, 10])
			space.area_sqm = random.randint(25, 35)
			space.floor = f"{random.randint(2, 4)}th Floor"
			space.status = "Available"
			space.description = f"Professional meeting room with video conferencing"
			space.use_custom_pricing = 0

			space.requires_fingerprint = 1
			space.door_number = f"MR-{i:02d}"
			space.insert(ignore_permissions=True)
			spaces.append(space.name)
			space_counter += 1

	print(f"  ✓ Created {len(spaces)} spaces across all locations")
	frappe.db.commit()
	return spaces


def create_members():
	"""Create Members with ALL fields"""
	print("\n👥 Creating Members...")

	members_data = [
		{
			"member_name": "Ahmed Mohammed Al-Rashid",
			"member_code": "MEM-001",
			"member_type": "Individual",
			"primary_email": "ahmed.rashid@techmail.com",
			"primary_mobile": "+966-50-1234567",
			"secondary_phone": "+966-11-2223333",
			"website": "https://ahmed-consulting.com",
			"join_date": add_days(nowdate(), -90),
			"status": "Active",
			"id_type": "National ID",
			"idcr_number": "1023456789",
			"id_expiry": add_days(nowdate(), 365),
			"industry": "Technology",
			"default_currency": "SAR"
		},
		{
			"member_name": "TechStart Solutions LLC",
			"member_code": "MEM-002",
			"member_type": "Company",
			"primary_email": "info@techstart.sa",
			"primary_mobile": "+966-50-9876543",
			"secondary_phone": "+966-11-4445555",
			"website": "https://techstart.sa",
			"join_date": add_days(nowdate(), -60),
			"status": "Active",
			"id_type": "CR",
			"idcr_number": "7012345678",
			"tax_id": "300123456700003",
			"industry": "Technology",
			"default_currency": "SAR",
			"credit_limit": 50000
		},
		{
			"member_name": "Sara Abdullah Al-Mansour",
			"member_code": "MEM-003",
			"member_type": "Individual",
			"primary_email": "sara.mansour@designstudio.com",
			"primary_mobile": "+966-55-1112233",
			"join_date": add_days(nowdate(), -30),
			"status": "Active",
			"id_type": "National ID",
			"idcr_number": "1087654321",
			"id_expiry": add_days(nowdate(), 730),
			"industry": "Marketing",
			"default_currency": "SAR"
		},
		{
			"member_name": "Global Consulting Partners",
			"member_code": "MEM-004",
			"member_type": "Company",
			"primary_email": "contact@globalcp.sa",
			"primary_mobile": "+966-50-5556677",
			"secondary_phone": "+966-11-6667777",
			"website": "https://globalcp.sa",
			"join_date": add_days(nowdate(), -120),
			"status": "Active",
			"id_type": "CR",
			"idcr_number": "7098765432",
			"tax_id": "300987654300003",
			"industry": "Consulting",
			"default_currency": "SAR",
			"credit_limit": 100000
		},
		{
			"member_name": "Khalid Fahd Al-Otaibi",
			"member_code": "MEM-005",
			"member_type": "Individual",
			"primary_email": "khalid.otaibi@lawfirm.sa",
			"primary_mobile": "+966-55-9998877",
			"join_date": add_days(nowdate(), -15),
			"status": "Active",
			"id_type": "National ID",
			"idcr_number": "1056781234",
			"id_expiry": add_days(nowdate(), 500),
			"industry": "Legal Services",
			"default_currency": "SAR"
		}
	]

	members = []
	for mem_data in members_data:
		if not frappe.db.exists("Member", mem_data["member_code"]):
			member = frappe.new_doc("Member")
			member.update(mem_data)
			member.insert(ignore_permissions=True)
			members.append(member.name)
			print(f"  ✓ Member: {member.member_name} ({member.member_code})")
			print(f"    - Customer: {member.customer}")
			print(f"    - ZK User ID: {member.zk_user_id}")
		else:
			# Member already exists
			members.append(mem_data["member_code"])

	frappe.db.commit()
	return members


def create_packages(locations):
	"""Create membership packages using ERPNext Package with custom fields"""
	print("\n📦 Creating Packages...")

	# Package names can only contain letters, digits, and hyphens (Frappe validation)
	# Custom required fields: description, package_code, package_category, status
	packages_data = [
		{
			"package_name": "flexidesk10days",
			"package_code": "FD10",
			"description": "10 days access to hot desks per month",
			"package_category": "Hot Desk",
			"status": "Active",
			"validity_days": 30,
			"price": 2500
		},
		{
			"package_name": "flexidesk20days",
			"package_code": "FD20",
			"description": "20 days access to hot desks per month",
			"package_category": "Hot Desk",
			"status": "Active",
			"validity_days": 30,
			"price": 4500
		},
		{
			"package_name": "meetingroom10hours",
			"package_code": "MR10",
			"description": "10 hours meeting room access per month",
			"package_category": "Meeting Room",
			"status": "Active",
			"validity_days": 30,
			"price": 1200
		},
		{
			"package_name": "dedicateddesk",
			"package_code": "DD",
			"description": "Full month dedicated desk access",
			"package_category": "Dedicated",
			"status": "Active",
			"validity_days": 30,
			"price": 3500
		},
		{
			"package_name": "privateoffice",
			"package_code": "PO",
			"description": "Private office monthly rental",
			"package_category": "Private Office",
			"status": "Active",
			"validity_days": 30,
			"price": 8000
		}
	]

	packages = []
	for pkg_data in packages_data:
		pkg_name = pkg_data["package_name"]
		if not frappe.db.exists("Package", pkg_name):
			package = frappe.new_doc("Package")
			package.name = pkg_name  # Explicitly set name for Prompt autoname
			package.package_name = pkg_name  # Must match naming constraints
			package.package_code = pkg_data["package_code"]
			package.description = pkg_data["description"]
			package.package_category = pkg_data["package_category"]
			package.status = pkg_data["status"]
			package.insert(ignore_permissions=True)
			packages.append(package.name)
			print(f"  ✓ Package: {package.package_name} ({pkg_data['package_code']})")

	frappe.db.commit()
	return packages


def create_access_devices(locations):
	"""Create Access Devices with ALL fields"""
	print("\n🔐 Creating Access Devices...")

	devices = []
	device_types = ["Fingerprint", "Face Recognition", "Card Reader"]
	device_counter = 1

	for location in locations:
		loc_name = frappe.db.get_value("GRM Location", location, "location_name")
		loc_code = frappe.db.get_value("GRM Location", location, "location_code")

		# Main entrance - Direct ZK
		device_code = f"ZK-{loc_code}-001"
		existing = frappe.db.exists("Access Device", {"device_code": device_code})
		if existing:
			devices.append(existing)
		else:
			device = frappe.new_doc("Access Device")
			device.device_name = f"{loc_name} - Main Entrance"
			device.device_code = device_code
			device.device_type = "Fingerprint"
			device.location = location
			device.model = "ZKTeco F18"
			device.serial_number = f"ZK{random.randint(100000, 999999)}"
			device.connection_mode = "Direct ZK"
			device.ip_address = f"192.168.{random.randint(1, 10)}.{random.randint(100, 200)}"
			device.port = 4370
			device.status = "Offline"
			device.auto_sync = 1
			device.sync_interval_minutes = 60
			device.insert(ignore_permissions=True)
			devices.append(device.name)
			device_counter += 1
			print(f"  ✓ Device: {device.device_name} ({device.device_code})")

		# Secondary entrance - BioTime API
		device_code2 = f"BIO-{loc_code}-002"
		existing2 = frappe.db.exists("Access Device", {"device_code": device_code2})
		if existing2:
			devices.append(existing2)
		else:
			device2 = frappe.new_doc("Access Device")
			device2.device_name = f"{loc_name} - Secondary Entrance"
			device2.device_code = device_code2
			device2.device_type = "Face Recognition"
			device2.location = location
			device2.model = "ZKTeco ProFace X"
			device2.serial_number = f"PF{random.randint(100000, 999999)}"
			device2.ip_address = f"192.168.1.{20 + device_counter}"  # Required field
			device2.port = 4370  # Required field
			device2.connection_mode = "BioTime API"
			device2.use_biotime = 1
			device2.biotime_device_serial = device2.serial_number
			device2.status = "Online"
			device2.auto_sync = 1
			device2.sync_interval_minutes = 30
			device2.insert(ignore_permissions=True)
			devices.append(device2.name)
			device_counter += 1
			print(f"  ✓ Device: {device2.device_name} ({device2.device_code})")

	frappe.db.commit()
	return devices


def create_contracts(members, spaces):
	"""Create Contracts with ALL fields"""
	print("\n📄 Creating Contracts...")

	contracts = []

	# Contract 1: Active contract for first member
	if len(members) > 0 and len(spaces) > 0:
		po_spaces = [s for s in spaces if "-PO" in s]
		if not po_spaces:
			print("  ! No private offices available for contract")
		else:
			contract_number = f"CTR-TEST-001"
			if frappe.db.exists("GRM Contract", {"contract_number": contract_number}):
				contracts.append(frappe.db.get_value("GRM Contract", {"contract_number": contract_number}, "name"))
				print(f"  Contract {contract_number} already exists")
			else:
				contract = frappe.new_doc("GRM Contract")
				contract.contract_number = contract_number
				contract.member = members[0]
				contract.contract_type = "Space Rental"
				contract.status = "Draft"
				contract.start_date = add_days(nowdate(), -30)
				contract.end_date = add_months(nowdate(), 5)
				contract.monthly_rent = 12000
				contract.security_deposit = 12000
				contract.notice_period_days = 30
				contract.auto_renew = 0
				contract.renewal_terms = "Negotiate"

				# Add space with explicit name for child table
				space_row = contract.append("spaces", {})
				space_row.name = f"{contract_number}-SP1"
				space_row.space = po_spaces[0]
				space_row.monthly_rent = 12000

				contract.insert(ignore_permissions=True)

				# Get member name for printing
				member_doc = frappe.get_doc("Member", members[0])

				# Try to approve contract if method exists
				try:
					if hasattr(contract, 'approve'):
						contract.approve()
				except Exception:
					pass  # Approval may require additional setup
				contracts.append(contract.name)
				print(f"  ✓ Contract: {contract.name} - {member_doc.member_name}")
				print(f"    - Status: {contract.status}")
				print(f"    - Monthly Rent: {contract.monthly_rent} SAR")

	frappe.db.commit()
	return contracts


def create_memberships(members, packages):
	"""Create Memberships with ALL fields"""
	print("\n🎫 Creating Memberships...")

	memberships = []

	# Membership for third member
	if len(members) > 2 and len(packages) > 0:
		membership = frappe.new_doc("Membership")
		membership.member = members[2]
		membership.package = packages[0]  # Flexi Desk - 10 Days
		membership.status = "Draft"
		membership.start_date = add_days(nowdate(), -15)
		membership.end_date = add_days(nowdate(), 15)
		membership.package_price = 2500
		membership.discount_percent = 10
		membership.total_access_allowed = 10
		membership.insert(ignore_permissions=True)

		# Activate membership
		membership.activate()

		# Use some access
		membership.decrement_access(3)

		memberships.append(membership.name)
		member_doc = frappe.get_doc("Member", members[2])
		print(f"  ✓ Membership: {membership.name} - {member_doc.member_name}")
		print(f"    - Package: {membership.package}")
		print(f"    - Access Used: {membership.access_used}/{membership.total_access_allowed}")

	frappe.db.commit()
	return memberships


def create_bookings(members, spaces):
	"""Create Bookings with ALL fields"""
	print("\n📅 Creating Bookings...")

	bookings = []

	# Get hot desks and meeting rooms
	hd_spaces = [s for s in spaces if "-HD" in s]
	mr_spaces = [s for s in spaces if "-MR" in s]

	# Booking 1: Future confirmed booking
	if len(members) > 1 and len(hd_spaces) > 0:
		booking_number = "BKG-TEST-001"
		if frappe.db.exists("Booking", {"booking_number": booking_number}):
			bookings.append(frappe.db.get_value("Booking", {"booking_number": booking_number}, "name"))
			print(f"  Booking {booking_number} already exists")
		else:
			booking = frappe.new_doc("Booking")
			booking.booking_number = booking_number
			booking.member = members[1]
			booking.booking_type = "Daily"
			booking.status = "Draft"
			booking.source = "Online"
			booking.space = hd_spaces[0]
			booking.booking_date = add_days(nowdate(), 3)
			booking.start_time = "09:00:00"
			booking.end_time = "17:00:00"
			booking.rate_type = "Daily Rate"
			booking.daily_rate = 300
			booking.insert(ignore_permissions=True)
			try:
				if hasattr(booking, 'confirm'):
					booking.confirm()
			except Exception:
				pass
			bookings.append(booking.name)
			print(f"  ✓ Booking: {booking.name} - {booking.space}")
			print(f"    - Date: {booking.booking_date}")
			print(f"    - Status: {booking.status}")

	# Booking 2: Today's checked-in booking
	if len(members) > 3 and len(mr_spaces) > 0:
		booking_number = "BKG-TEST-002"
		if frappe.db.exists("Booking", {"booking_number": booking_number}):
			bookings.append(frappe.db.get_value("Booking", {"booking_number": booking_number}, "name"))
			print(f"  Booking {booking_number} already exists")
		else:
			booking = frappe.new_doc("Booking")
			booking.booking_number = booking_number
			booking.member = members[3]
			booking.booking_type = "Hourly"
			booking.status = "Draft"
			booking.source = "Walk-in"
			booking.space = mr_spaces[0]
			booking.booking_date = nowdate()
			booking.start_time = "10:00:00"
			booking.end_time = "14:00:00"
			booking.rate_type = "Hourly Rate"
			booking.hourly_rate = 150
			booking.insert(ignore_permissions=True)
			try:
				if hasattr(booking, 'confirm'):
					booking.confirm()
				if hasattr(booking, 'check_in'):
					booking.check_in()
			except Exception:
				pass
			bookings.append(booking.name)
			print(f"  ✓ Booking: {booking.name} - {booking.space}")
			print(f"    - Status: {booking.status}")

	frappe.db.commit()
	return bookings


def create_location_expenses(locations):
	"""Create Location Expenses with ALL fields"""
	print("\n💰 Creating Location Expenses...")

	expenses = []
	expense_types = [
		("Rent", "Property Landlord Co.", 80000),
		("Electricity", "Power & Water Authority", 12000),
		("Water", "Power & Water Authority", 3000),
		("Internet", "Internet Service Provider", 2000),
		("Cleaning", "Cleaning Services Ltd.", 8000),
		("Maintenance", "Maintenance & Repairs Inc.", 5000)
	]

	for location in locations[:1]:  # Create for first location only
		for exp_type, vendor, amount in expense_types:
			expense = frappe.new_doc("Location Expense")
			expense.location = location
			expense.expense_date = nowdate()
			expense.expense_type = exp_type
			expense.amount = amount
			expense.vendor = vendor
			expense.description = f"{exp_type} expense for {frappe.utils.formatdate(nowdate(), 'MMMM yyyy')}"
			expense.payment_status = "Paid" if random.choice([True, False]) else "Pending"
			expense.invoice_number = f"{exp_type[:3].upper()}-{nowdate().replace('-', '')}-001"
			expense.is_recurring = 1 if exp_type in ["Rent", "Internet"] else 0

			if expense.is_recurring:
				from datetime import datetime
				expense.period_month = datetime.now().strftime("%B")
				expense.period_year = datetime.now().year

			expense.insert(ignore_permissions=True)

			# Create Purchase Invoice and Payment if configured
			try:
				if expense.payment_status == "Paid":
					expense.payment_date = nowdate()
					expense.save()
					result = expense.auto_create_invoice_and_payment()
					print(f"  ✓ Expense: {expense.name} - {exp_type} ({amount} SAR)")
					print(f"    - PI: {result.get('purchase_invoice')}")
					print(f"    - Payment: {result.get('payment_entry')}")
				else:
					expense.create_purchase_invoice()
					print(f"  ✓ Expense: {expense.name} - {exp_type} ({amount} SAR)")
					print(f"    - PI: {expense.purchase_invoice} (Unpaid)")

				expenses.append(expense.name)
			except Exception as e:
				print(f"  ⚠ Expense created but financial docs failed: {str(e)[:100]}")
				expenses.append(expense.name)

	frappe.db.commit()
	return expenses


def create_biotime_settings():
	"""Create/Update BioTime Settings"""
	print("\n⚙️  Configuring BioTime Settings...")

	if not frappe.db.exists("BioTime Settings", "BioTime Settings"):
		biotime = frappe.new_doc("BioTime Settings")
	else:
		biotime = frappe.get_doc("BioTime Settings", "BioTime Settings")

	biotime.enabled = 0  # Disabled by default (requires real server)
	biotime.server_url = "192.168.1.10"
	biotime.port = 8000
	biotime.username = "admin"
	biotime.password = "test_password"  # Required field - use test password
	biotime.auto_sync = 0
	biotime.sync_interval_minutes = 60
	biotime.batch_size = 100
	biotime.save(ignore_permissions=True)

	print(f"  ✓ BioTime Settings configured (Disabled - requires real server)")
	frappe.db.commit()


def print_summary(locations, space_types, spaces, members, contracts, memberships, bookings, devices, expenses):
	"""Print summary of created data"""
	print("\n📊 SUMMARY:")
	print(f"  - Locations: {len(locations)}")
	print(f"  - Space Types: {len(space_types)}")
	print(f"  - Spaces: {len(spaces)}")
	print(f"  - Members: {len(members)}")
	print(f"  - Contracts: {len(contracts)}")
	print(f"  - Memberships: {len(memberships)}")
	print(f"  - Bookings: {len(bookings)}")
	print(f"  - Access Devices: {len(devices)}")
	print(f"  - Location Expenses: {len(expenses)}")

	# Get statistics
	print("\n📈 STATISTICS:")

	# Members
	active_members = frappe.db.count("Member", {"status": "Active"})
	print(f"  - Active Members: {active_members}")

	# Spaces
	available_spaces = frappe.db.count("Space", {"status": "Available"})
	occupied_spaces = frappe.db.count("Space", {"status": "Occupied"})
	print(f"  - Available Spaces: {available_spaces}")
	print(f"  - Occupied Spaces: {occupied_spaces}")

	# Contracts
	active_contracts = frappe.db.count("GRM Contract", {"status": "Active"})
	print(f"  - Active Contracts: {active_contracts}")

	# Invoices
	total_invoices = frappe.db.count("Sales Invoice")
	print(f"  - Total Sales Invoices: {total_invoices}")

	# Purchase Invoices
	total_pi = frappe.db.count("Purchase Invoice")
	print(f"  - Total Purchase Invoices: {total_pi}")

	# Access Rules
	active_rules = frappe.db.count("Access Rule", {"status": "Active"})
	print(f"  - Active Access Rules: {active_rules}")
