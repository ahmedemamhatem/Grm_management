"""
Test Data Generator for GRM Management (Coworking Space Management)

This script creates sample data for testing all features:
- Locations, Space Types, Spaces
- Members with ZK User IDs
- Packages, Contracts, Memberships
- Bookings
- Access Devices (Direct ZK and BioTime)
"""

import frappe
from frappe.utils import nowdate, add_days, add_months, now_datetime


def create_test_data():
	"""Create comprehensive test data"""
	print("\n" + "="*80)
	print("CREATING TEST DATA FOR GRM MANAGEMENT SYSTEM")
	print("="*80 + "\n")

	# Create in order due to dependencies
	create_locations()
	create_space_types()
	create_spaces()
	create_amenities()
	create_members()
	create_packages()
	create_access_devices()
	create_contracts()
	create_memberships()
	create_bookings()

	print("\n" + "="*80)
	print("TEST DATA CREATION COMPLETE!")
	print("="*80 + "\n")

	print_summary()


def create_locations():
	"""Create sample locations"""
	print("📍 Creating Locations...")

	locations = [
		{
			"location_name": "Downtown Branch",
			"location_code": "DT-001",
			"status": "Active",
			"address": "123 Main Street, Downtown",
			"city": "Riyadh",
			"country": "Saudi Arabia"
		},
		{
			"location_name": "Tech Park Branch",
			"location_code": "TP-001",
			"status": "Active",
			"address": "456 Innovation Ave, Tech Park",
			"city": "Riyadh",
			"country": "Saudi Arabia"
		}
	]

	for loc_data in locations:
		if not frappe.db.exists("GRM Location", loc_data["location_code"]):
			try:
				loc = frappe.new_doc("GRM Location")
				loc.update(loc_data)
				loc.insert(ignore_permissions=True)
				print(f"  ✓ Created GRM Location: {loc.location_name}")
			except Exception as e:
				print(f"  ✗ Error creating {loc_data['location_name']}: {e}")

	frappe.db.commit()


def create_space_types():
	"""Create sample space types"""
	print("\n🏢 Creating Space Types...")

	space_types = [
		{
			"type_name": "Private Office",
			"type_code": "PO",
			"allow_hourly": 0,
			"allow_daily": 1,
			"allow_monthly": 1,
			"hourly_rate": 0,
			"daily_rate": 500,
			"monthly_rate": 10000
		},
		{
			"type_name": "Hot Desk",
			"type_code": "HD",
			"allow_hourly": 1,
			"allow_daily": 1,
			"allow_monthly": 1,
			"hourly_rate": 50,
			"daily_rate": 300,
			"monthly_rate": 5000
		},
		{
			"type_name": "Meeting Room",
			"type_code": "MR",
			"allow_hourly": 1,
			"allow_daily": 1,
			"allow_monthly": 0,
			"hourly_rate": 100,
			"daily_rate": 800,
			"monthly_rate": 0
		}
	]

	for st_data in space_types:
		if not frappe.db.exists("Space Type", st_data["type_name"]):
			try:
				st = frappe.new_doc("Space Type")
				st.update(st_data)
				st.insert(ignore_permissions=True)
				print(f"  ✓ Created Space Type: {st.type_name}")
			except Exception as e:
				print(f"  ✗ Error creating {st_data['type_name']}: {e}")

	frappe.db.commit()


def create_spaces():
	"""Create sample spaces"""
	print("\n🚪 Creating Spaces...")

	spaces = [
		# Downtown Branch
		{"space_name": "Office A-101", "space_code": "DT-A101", "location": "Downtown Branch",
		 "space_type": "Private Office", "capacity": 4, "status": "Available"},
		{"space_name": "Office A-102", "space_code": "DT-A102", "location": "Downtown Branch",
		 "space_type": "Private Office", "capacity": 6, "status": "Available"},
		{"space_name": "Hot Desk 1", "space_code": "DT-HD01", "location": "Downtown Branch",
		 "space_type": "Hot Desk", "capacity": 1, "status": "Available"},
		{"space_name": "Meeting Room 1", "space_code": "DT-MR01", "location": "Downtown Branch",
		 "space_type": "Meeting Room", "capacity": 8, "status": "Available"},

		# Tech Park Branch
		{"space_name": "Office B-201", "space_code": "TP-B201", "location": "Tech Park Branch",
		 "space_type": "Private Office", "capacity": 5, "status": "Available"},
		{"space_name": "Hot Desk 1", "space_code": "TP-HD01", "location": "Tech Park Branch",
		 "space_type": "Hot Desk", "capacity": 1, "status": "Available"},
	]

	for space_data in spaces:
		if not frappe.db.exists("Space", space_data["space_code"]):
			try:
				space = frappe.new_doc("Space")
				space.update(space_data)
				space.insert(ignore_permissions=True)
				print(f"  ✓ Created Space: {space.space_name} ({space.space_code})")
			except Exception as e:
				print(f"  ✗ Error creating {space_data['space_name']}: {e}")

	frappe.db.commit()


def create_amenities():
	"""Create sample amenities"""
	print("\n🎯 Creating Amenities...")

	amenities = [
		{"amenity_name": "High-Speed WiFi", "category": "Internet", "is_chargeable": 0},
		{"amenity_name": "Printing Service", "category": "Office", "is_chargeable": 1, "price": 1},
		{"amenity_name": "Coffee & Tea", "category": "Refreshments", "is_chargeable": 0},
		{"amenity_name": "Parking Spot", "category": "Parking", "is_chargeable": 1, "price": 200},
	]

	for amenity_data in amenities:
		if not frappe.db.exists("Amenity", amenity_data["amenity_name"]):
			try:
				amenity = frappe.new_doc("Amenity")
				amenity.update(amenity_data)
				amenity.insert(ignore_permissions=True)
				print(f"  ✓ Created Amenity: {amenity.amenity_name}")
			except Exception as e:
				print(f"  ✗ Error creating {amenity_data['amenity_name']}: {e}")

	frappe.db.commit()


def create_members():
	"""Create sample members with ZK User IDs"""
	print("\n👥 Creating Members...")

	members = [
		{
			"member_name": "Ahmed Al-Rashid",
			"member_code": "MEM-001",
			"member_type": "Individual",
			"primary_email": "ahmed@example.com",
			"primary_mobile": "+966501234567",
			"join_date": nowdate(),
			"status": "Active",
			"zk_user_id": "1001"  # Will be auto-generated if not set
		},
		{
			"member_name": "Sarah Tech Solutions",
			"member_code": "MEM-002",
			"member_type": "Company",
			"primary_email": "info@sarahtech.com",
			"primary_mobile": "+966507654321",
			"join_date": nowdate(),
			"status": "Active",
			"zk_user_id": "1002"
		},
		{
			"member_name": "Mohammed Hassan",
			"member_code": "MEM-003",
			"member_type": "Individual",
			"primary_email": "mohammed@example.com",
			"primary_mobile": "+966509876543",
			"join_date": nowdate(),
			"status": "Active",
			"zk_user_id": "1003"
		},
	]

	for member_data in members:
		if not frappe.db.exists("Member", {"primary_email": member_data["primary_email"]}):
			try:
				member = frappe.new_doc("Member")
				member.update(member_data)
				member.insert(ignore_permissions=True)
				print(f"  ✓ Created Member: {member.member_name} (ZK ID: {member.zk_user_id})")
			except Exception as e:
				print(f"  ✗ Error creating {member_data['member_name']}: {e}")

	frappe.db.commit()


def create_packages():
	"""Create sample membership packages"""
	print("\n📦 Creating Packages...")

	# Note: Package DocType may have different structure
	# This is a placeholder - adjust based on actual Package fields
	print("  ⚠ Package creation skipped - please create manually in UI")


def create_access_devices():
	"""Create sample access devices (Direct ZK and BioTime)"""
	print("\n🔐 Creating Access Devices...")

	devices = [
		{
			"device_name": "Downtown Main Entrance ZK",
			"device_code": "ZK-DT-001",
			"device_type": "Fingerprint",
			"location": "Downtown Branch",
			"connection_mode": "Direct ZK",
			"ip_address": "192.168.1.100",
			"port": 4370,
			"status": "Offline",
			"auto_sync": 1
		},
		{
			"device_name": "Tech Park Entry (BioTime)",
			"device_code": "BIO-TP-001",
			"device_type": "Face Recognition",
			"location": "Tech Park Branch",
			"connection_mode": "BioTime API",
			"serial_number": "DGD9190019050335644",
			"status": "Online",
			"auto_sync": 1
		}
	]

	for device_data in devices:
		if not frappe.db.exists("Access Device", device_data["device_code"]):
			try:
				device = frappe.new_doc("Access Device")
				device.update(device_data)
				device.insert(ignore_permissions=True)
				print(f"  ✓ Created Access Device: {device.device_name} ({device.connection_mode})")
			except Exception as e:
				print(f"  ✗ Error creating {device_data['device_name']}: {e}")

	frappe.db.commit()


def create_contracts():
	"""Create sample contracts"""
	print("\n📄 Creating Contracts...")

	# Get first member
	member = frappe.db.get_value("Member", {"member_code": "MEM-001"}, "name")
	if not member:
		print("  ⚠ No members found. Skipping contract creation.")
		return

	contracts = [
		{
			"member": member,
			"contract_type": "Space Rental",
			"status": "Draft",
			"start_date": nowdate(),
			"end_date": add_months(nowdate(), 6),
			"monthly_rent": 10000,
			"security_deposit": 10000,
			"deposit_status": "Pending"
		}
	]

	for contract_data in contracts:
		try:
			contract = frappe.new_doc("GRM Contract")
			contract.update(contract_data)

			# Add space
			contract.append("spaces", {
				"space": frappe.db.get_value("Space", {"space_code": "DT-A101"}, "name"),
				"monthly_rent": 10000
			})

			contract.insert(ignore_permissions=True)
			print(f"  ✓ Created Contract: {contract.contract_number} for {contract.member}")
		except Exception as e:
			print(f"  ✗ Error creating contract: {e}")

	frappe.db.commit()


def create_memberships():
	"""Create sample memberships"""
	print("\n🎫 Creating Memberships...")
	print("  ⚠ Membership creation requires Package - create manually in UI")


def create_bookings():
	"""Create sample bookings"""
	print("\n📅 Creating Bookings...")

	# Get member and space
	member = frappe.db.get_value("Member", {"member_code": "MEM-003"}, "name")
	meeting_room = frappe.db.get_value("Space", {"space_code": "DT-MR01"}, "name")

	if not member or not meeting_room:
		print("  ⚠ Member or Meeting Room not found. Skipping booking creation.")
		return

	bookings = [
		{
			"member": member,
			"space": meeting_room,
			"booking_date": add_days(nowdate(), 2),
			"start_time": "09:00:00",
			"end_time": "12:00:00",
			"rate_type": "Hourly Rate",
			"status": "Draft"
		}
	]

	for booking_data in bookings:
		try:
			booking = frappe.new_doc("Booking")
			booking.update(booking_data)
			booking.insert(ignore_permissions=True)
			print(f"  ✓ Created Booking: {booking.name} for {booking.booking_date}")
		except Exception as e:
			print(f"  ✗ Error creating booking: {e}")

	frappe.db.commit()


def print_summary():
	"""Print summary of created test data"""
	print("\n📊 TEST DATA SUMMARY")
	print("-" * 80)

	counts = {
		"Location": frappe.db.count("Location"),
		"Space Type": frappe.db.count("Space Type"),
		"Space": frappe.db.count("Space"),
		"Amenity": frappe.db.count("Amenity"),
		"Member": frappe.db.count("Member"),
		"Access Device": frappe.db.count("Access Device"),
		"GRM Contract": frappe.db.count("GRM Contract"),
		"Booking": frappe.db.count("Booking"),
	}

	for doctype, count in counts.items():
		print(f"  {doctype:20} : {count:3} records")

	print("\n💡 NEXT STEPS:")
	print("  1. Configure BioTime Settings (if using BioTime API)")
	print("  2. Create Packages for Memberships")
	print("  3. Approve Draft Contracts")
	print("  4. Create Memberships")
	print("  5. Test Access Device sync")
	print("-" * 80)


def run():
	"""Entry point for bench execute"""
	create_test_data()


if __name__ == "__main__":
	run()
