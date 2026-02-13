# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url, cstr, strip_html


def _msg(en, ar):
	"""Return bilingual message dict."""
	return {"en": en, "ar": ar}


def _sanitize_text(value, max_length=500):
	"""Strip HTML tags and limit length to prevent XSS / abuse."""
	if not value:
		return None
	return cstr(strip_html(cstr(value)))[:max_length]


def get_full_image_url(image_path):
	"""Convert relative image path to full URL

	Args:
		image_path: Relative path like /files/image.jpg

	Returns:
		str: Full URL like https://example.com/files/image.jpg
	"""
	if not image_path:
		return None

	# If already a full URL, return as is
	if image_path.startswith("http://") or image_path.startswith("https://"):
		return image_path

	# Get the site URL and append the image path
	site_url = get_url()

	# Ensure no double slashes
	if image_path.startswith("/"):
		return f"{site_url}{image_path}"
	else:
		return f"{site_url}/{image_path}"


@frappe.whitelist(allow_guest=True)
def get_spaces_by_type(location=None, status=None):
	"""Get GRM Spaces grouped by GRM Space Type

	This endpoint is publicly accessible (no authentication required).
	Returns spaces with human-readable names instead of IDs.

	Args:
		location: Filter by location name (optional)
		status: Filter by space status (optional) - Available, Rented, Not Ready, Under Maintenance, Reserved

	Returns:
		dict: Spaces grouped by space type with names

	Example Response:
		{
			"success": true,
			"data": {
				"Private Office": {
					"type_info": {
						"name": "Private Office",
						"name_ar": "مكتب خاص",
						"category": "Private Office",
						"icon": "office",
						"color": "#4CAF50"
					},
					"spaces": [
						{
							"name": "SPACE-2026-0001",
							"space_name": "Executive Office A",
							"space_name_ar": "المكتب التنفيذي أ",
							"location": "Main Branch",
							"property": "Building A",
							"status": "Available",
							"capacity": 4,
							"area_sqm": 25.0,
							"hourly_rate": 100,
							"daily_rate": 500,
							"monthly_rate": 5000,
							"space_image": "/files/office-a.jpg",
							"amenities": ["WiFi", "Air Conditioning", "Projector"]
						}
					],
					"count": 1
				}
			},
			"total_spaces": 1,
			"total_types": 1
		}
	"""
	try:
		# Sanitize inputs
		if location:
			location = _sanitize_text(location, 140)
		if status:
			status = _sanitize_text(status, 30)

		# Whitelist valid statuses
		valid_statuses = ("Available", "Rented", "Not Ready", "Under Maintenance", "Reserved")
		if status and status not in valid_statuses:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg(
					f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
					f"حالة غير صالحة. يجب أن تكون واحدة من: {', '.join(valid_statuses)}"
				),
			}

		# Build filters for spaces
		filters = {}

		if location:
			# Get location by name if passed
			location_exists = frappe.db.exists("GRM Location", {"name": location})
			if not location_exists:
				# Try to find by location name
				location_doc = frappe.db.get_value("GRM Location", {"location_name": location}, "name")
				if location_doc:
					filters["location"] = location_doc
				else:
					frappe.response["http_status_code"] = 404
					return {
						"success": False,
						"http_status_code": 404,
						"message": _msg("Location not found", "الموقع غير موجود"),
					}
			else:
				filters["location"] = location

		if status:
			filters["status"] = status

		# Get all spaces with required fields
		spaces = frappe.get_all(
			"GRM Space",
			filters=filters,
			fields=[
				"name",
				"space_name",
				"space_name_ar",
				"space_code",
				"location",
				"property",
				"space_type",
				"status",
				"is_featured",
				"allow_booking",
				"floor_number",
				"room_number",
				"area_sqm",
				"capacity",
				"min_booking_hours",
				"hourly_rate",
				"daily_rate",
				"monthly_rate",
				"annual_rate",
				"minimum_charge",
				"wifi",
				"air_conditioning",
				"projector",
				"whiteboard",
				"coffee_tea",
				"parking",
				"printer_access",
				"phone_line",
				"custom_amenities",
				"description",
				"space_image"
			],
			order_by="space_name asc"
		)

		# Get all active space types
		space_types = frappe.get_all(
			"GRM Space Type",
			filters={"is_active": 1},
			fields=[
				"name",
				"space_type_name",
				"space_type_name_ar",
				"category",
				"icon",
				"color_code",
				"default_capacity",
				"typical_area_sqm",
				"description",
				"default_amenities",
				"typical_usage"
			],
			order_by="space_type_name asc"
		)

		# Create a mapping for space types
		type_map = {st.name: st for st in space_types}

		# Group spaces by type
		grouped_data = {}

		for space in spaces:
			space_type_id = space.get("space_type")

			if space_type_id not in grouped_data:
				type_info = type_map.get(space_type_id, {})
				grouped_data[space_type_id] = {
					"type_info": {
						"name": type_info.get("space_type_name", space_type_id),
						"name_ar": type_info.get("space_type_name_ar", ""),
						"category": type_info.get("category", ""),
						"icon": type_info.get("icon", ""),
						"color": type_info.get("color_code", ""),
						"description": type_info.get("description", ""),
						"typical_usage": type_info.get("typical_usage", "")
					},
					"spaces": [],
					"count": 0
				}

			# Build amenities list
			amenities = []
			if space.get("wifi"):
				amenities.append("WiFi")
			if space.get("air_conditioning"):
				amenities.append("Air Conditioning")
			if space.get("projector"):
				amenities.append("Projector")
			if space.get("whiteboard"):
				amenities.append("Whiteboard")
			if space.get("coffee_tea"):
				amenities.append("Coffee/Tea")
			if space.get("parking"):
				amenities.append("Parking")
			if space.get("printer_access"):
				amenities.append("Printer Access")
			if space.get("phone_line"):
				amenities.append("Phone Line")

			# Get location name (EN + AR)
			location_name = ""
			location_name_ar = ""
			if space.get("location"):
				loc_info = frappe.db.get_value(
					"GRM Location", space.get("location"),
					["location_name", "location_name_ar"], as_dict=True
				)
				if loc_info:
					location_name = loc_info.location_name or space.get("location")
					location_name_ar = loc_info.location_name_ar or ""

			# Get property name
			property_name = ""
			if space.get("property"):
				property_name = frappe.db.get_value("GRM Property", space.get("property"), "property_name") or space.get("property")

			# Build full image URL
			image_url = get_full_image_url(space.get("space_image"))

			# Build space data with names instead of IDs
			space_data = {
				"id": space.get("name"),
				"space_name": space.get("space_name"),
				"space_name_ar": space.get("space_name_ar"),
				"space_code": space.get("space_code"),
				"location": location_name,
				"location_ar": location_name_ar,
				"property": property_name,
				"status": space.get("status"),
				"is_featured": space.get("is_featured"),
				"allow_booking": space.get("allow_booking"),
				"floor_number": space.get("floor_number"),
				"room_number": space.get("room_number"),
				"area_sqm": space.get("area_sqm"),
				"capacity": space.get("capacity"),
				"min_booking_hours": space.get("min_booking_hours"),
				"hourly_rate": space.get("hourly_rate"),
				"daily_rate": space.get("daily_rate"),
				"monthly_rate": space.get("monthly_rate"),
				"annual_rate": space.get("annual_rate"),
				"minimum_charge": space.get("minimum_charge"),
				"amenities": amenities,
				"custom_amenities": space.get("custom_amenities"),
				"description": space.get("description"),
				"space_image": image_url
			}

			grouped_data[space_type_id]["spaces"].append(space_data)
			grouped_data[space_type_id]["count"] += 1

		# Convert to list with type names as keys for cleaner response
		result_data = {}
		for type_id, type_data in grouped_data.items():
			type_name = type_data["type_info"]["name"]
			result_data[type_name] = type_data

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Spaces retrieved successfully", "تم جلب المساحات بنجاح"),
			"data": result_data,
			"total_spaces": len(spaces),
			"total_types": len(result_data),
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Spaces API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}

@frappe.whitelist(allow_guest=True)
def get_space_by_id(id=None):
	"""Get single GRM Space by ID (DocName), e.g. SPACE-2026-0004"""
	try:
		if not id:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("Missing id", "حقل id مطلوب"),
			}

		id = _sanitize_text(id, 140)

		# Fetch the space
		space = frappe.db.get_value(
			"GRM Space",
			id,
			[
				"name",
				"space_name",
				"space_name_ar",
				"space_code",
				"location",
				"property",
				"space_type",
				"status",
				"is_featured",
				"allow_booking",
				"floor_number",
				"room_number",
				"area_sqm",
				"capacity",
				"min_booking_hours",
				"hourly_rate",
				"daily_rate",
				"monthly_rate",
				"annual_rate",
				"minimum_charge",
				"wifi",
				"air_conditioning",
				"projector",
				"whiteboard",
				"coffee_tea",
				"parking",
				"printer_access",
				"phone_line",
				"custom_amenities",
				"description",
				"space_image",
			],
			as_dict=True
		)

		if not space:
			frappe.response["http_status_code"] = 404
			return {
				"success": False,
				"http_status_code": 404,
				"message": _msg("Space not found", "المساحة غير موجودة"),
			}

		# Get space type info (optional nice-to-have)
		type_info = {}
		if space.get("space_type"):
			type_info = frappe.db.get_value(
				"GRM Space Type",
				space.get("space_type"),
				[
					"name",
					"space_type_name",
					"space_type_name_ar",
					"category",
					"icon",
					"color_code",
					"description",
					"typical_usage",
				],
				as_dict=True
			) or {}

		# Build amenities list
		amenities = []
		if space.get("wifi"):
			amenities.append("WiFi")
		if space.get("air_conditioning"):
			amenities.append("Air Conditioning")
		if space.get("projector"):
			amenities.append("Projector")
		if space.get("whiteboard"):
			amenities.append("Whiteboard")
		if space.get("coffee_tea"):
			amenities.append("Coffee/Tea")
		if space.get("parking"):
			amenities.append("Parking")
		if space.get("printer_access"):
			amenities.append("Printer Access")
		if space.get("phone_line"):
			amenities.append("Phone Line")

		# Location name (EN + AR)
		location_name = ""
		location_name_ar = ""
		if space.get("location"):
			loc_info = frappe.db.get_value(
				"GRM Location",
				space.get("location"),
				["location_name", "location_name_ar"],
				as_dict=True
			)
			if loc_info:
				location_name = loc_info.location_name or space.get("location")
				location_name_ar = loc_info.location_name_ar or ""

		# Property name
		property_name = ""
		if space.get("property"):
			property_name = frappe.db.get_value(
				"GRM Property",
				space.get("property"),
				"property_name"
			) or space.get("property")

		# Full image URL
		image_url = get_full_image_url(space.get("space_image"))

		# Final response object
		space_data = {
			"id": space.get("name"),
			"space_name": space.get("space_name"),
			"space_name_ar": space.get("space_name_ar"),
			"space_code": space.get("space_code"),
			"location": location_name,
			"location_ar": location_name_ar,
			"property": property_name,
			"status": space.get("status"),
			"is_featured": space.get("is_featured"),
			"allow_booking": space.get("allow_booking"),
			"floor_number": space.get("floor_number"),
			"room_number": space.get("room_number"),
			"area_sqm": space.get("area_sqm"),
			"capacity": space.get("capacity"),
			"min_booking_hours": space.get("min_booking_hours"),
			"hourly_rate": space.get("hourly_rate"),
			"daily_rate": space.get("daily_rate"),
			"monthly_rate": space.get("monthly_rate"),
			"annual_rate": space.get("annual_rate"),
			"minimum_charge": space.get("minimum_charge"),
			"amenities": amenities,
			"custom_amenities": space.get("custom_amenities"),
			"description": space.get("description"),
			"space_image": image_url,
			"space_type": {
				"id": space.get("space_type"),
				"name": type_info.get("space_type_name", space.get("space_type") or ""),
				"name_ar": type_info.get("space_type_name_ar", ""),
				"category": type_info.get("category", ""),
				"icon": type_info.get("icon", ""),
				"color": type_info.get("color_code", ""),
				"description": type_info.get("description", ""),
				"typical_usage": type_info.get("typical_usage", ""),
			}
		}

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Space retrieved successfully", "تم جلب بيانات المساحة بنجاح"),
			"data": space_data,
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Space By ID API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist(allow_guest=True)
def get_space_types():
	"""Get all active GRM Space Types

	This endpoint is publicly accessible (no authentication required).

	Returns:
		dict: List of all active space types with details
	"""
	try:
		space_types = frappe.get_all(
			"GRM Space Type",
			filters={"is_active": 1},
			fields=[
				"name",
				"space_type_name",
				"space_type_name_ar",
				"space_type_code",
				"category",
				"icon",
				"color_code",
				"default_capacity",
				"min_capacity",
				"max_capacity",
				"typical_area_sqm",
				"hourly_rate",
				"daily_rate",
				"monthly_rate",
				"annual_rate",
				"description",
				"default_amenities",
				"typical_usage"
			],
			order_by="space_type_name asc"
		)

		# Transform to use names
		result = []
		for st in space_types:
			result.append({
				"id": st.get("name"),
				"name": st.get("space_type_name"),
				"name_ar": st.get("space_type_name_ar"),
				"code": st.get("space_type_code"),
				"category": st.get("category"),
				"icon": st.get("icon"),
				"color": st.get("color_code"),
				"default_capacity": st.get("default_capacity"),
				"min_capacity": st.get("min_capacity"),
				"max_capacity": st.get("max_capacity"),
				"typical_area_sqm": st.get("typical_area_sqm"),
				"hourly_rate": st.get("hourly_rate"),
				"daily_rate": st.get("daily_rate"),
				"monthly_rate": st.get("monthly_rate"),
				"annual_rate": st.get("annual_rate"),
				"description": st.get("description"),
				"default_amenities": st.get("default_amenities"),
				"typical_usage": st.get("typical_usage")
			})

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Space types retrieved successfully", "تم جلب أنواع المساحات بنجاح"),
			"data": result,
			"total": len(result),
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Spaces API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}
