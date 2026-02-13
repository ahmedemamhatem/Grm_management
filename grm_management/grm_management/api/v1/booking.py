# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import (
	nowdate, getdate, cint, flt, get_url, cstr, strip_html,
)
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers (private — not exposed via API)
# ---------------------------------------------------------------------------

def _msg(en, ar):
	"""Return bilingual message dict."""
	return {"en": en, "ar": ar}


def get_full_image_url(image_path):
	"""Convert relative image path to full URL"""
	if not image_path:
		return None
	if image_path.startswith("http://") or image_path.startswith("https://"):
		return image_path
	site_url = get_url()
	if image_path.startswith("/"):
		return f"{site_url}{image_path}"
	return f"{site_url}/{image_path}"


def _get_tenant_for_current_user():
	"""Get the GRM Tenant linked to the current logged-in user."""
	user = frappe.session.user
	if user in ("Administrator", "Guest"):
		return None
	user_email = frappe.db.get_value("User", user, "email") or user
	return frappe.db.get_value("GRM Tenant", {"primary_email": user_email}, "name")


def _sanitize_text(value, max_length=500):
	"""Strip HTML tags and limit length to prevent XSS / abuse."""
	if not value:
		return None
	return cstr(strip_html(cstr(value)))[:max_length]


def _validate_docname(value):
	"""Validate that a value looks like a safe Frappe document name.
	Prevents path traversal or injection via document name fields."""
	if not value:
		return None
	value = cstr(value).strip()
	# Frappe doc names should not contain slashes, angle brackets, etc.
	for char in ("/", "\\", "<", ">", '"', "'", ";", "`"):
		if char in value:
			frappe.throw(_("Invalid document reference"), frappe.ValidationError)
	return value


def _parse_time_string(time_str):
	"""Parse time string in various formats."""
	if not time_str:
		return None

	if hasattr(time_str, "hour"):
		return time_str

	time_str = cstr(time_str).strip()

	formats = ["%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p"]
	for fmt in formats:
		try:
			return datetime.strptime(time_str, fmt).time()
		except ValueError:
			continue

	parts = time_str.replace(":", " ").split()
	if len(parts) >= 2:
		try:
			hour = int(parts[0])
			minute = int(parts[1])
			return datetime(2000, 1, 1, hour, minute).time()
		except (ValueError, TypeError):
			pass

	frappe.throw(_("Invalid time format"), frappe.ValidationError)


def _calculate_duration_hours(start_time, end_time):
	"""Calculate duration in hours between two times."""
	start_t = _parse_time_string(start_time)
	end_t = _parse_time_string(end_time)

	start_dt = datetime(2000, 1, 1, start_t.hour, start_t.minute, getattr(start_t, "second", 0))
	end_dt = datetime(2000, 1, 1, end_t.hour, end_t.minute, getattr(end_t, "second", 0))

	duration = (end_dt - start_dt).total_seconds() / 3600
	return round(duration, 2)


def _require_auth():
	"""Return error dict if not authenticated, else None."""
	if frappe.session.user == "Guest":
		frappe.response["http_status_code"] = 401
		return {
			"success": False,
			"http_status_code": 401,
			"message": _msg("Authentication required", "يجب تسجيل الدخول"),
		}
	return None


def _get_space_location_name(location_id):
	"""Get location name from GRM Location safely."""
	if not location_id:
		return ""
	return frappe.db.get_value("GRM Location", location_id, "location_name") or location_id


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def check_availability(space=None, booking_date=None, start_time=None, end_time=None):
	"""Check if a space is available for booking at the specified time.

	Returns:
		200: Available + pricing
		400: Validation error
		404: Space not found
		409: Not available
		500: Server error
	"""
	try:
		# --- input validation ---
		space = _validate_docname(space)
		if not space or not booking_date or not start_time or not end_time:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("space, booking_date, start_time, and end_time are required", "المساحة وتاريخ الحجز ووقت البداية ووقت النهاية مطلوبون"),
			}

		if not frappe.db.exists("GRM Space", space):
			frappe.response["http_status_code"] = 404
			return {
				"success": False,
				"http_status_code": 404,
				"message": _msg("Space not found", "المساحة غير موجودة"),
			}

		space_doc = frappe.get_doc("GRM Space", space)

		if not space_doc.allow_booking:
			frappe.response["http_status_code"] = 409
			return {
				"success": False,
				"http_status_code": 409,
				"available": False,
				"message": _msg("This space does not allow bookings", "هذه المساحة لا تقبل الحجوزات"),
			}

		if space_doc.status != "Available":
			frappe.response["http_status_code"] = 409
			return {
				"success": False,
				"http_status_code": 409,
				"available": False,
				"message": _msg("Space is currently not available", "المساحة غير متاحة حالياً"),
			}

		# Parse & validate date
		try:
			booking_dt = getdate(booking_date)
		except Exception:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("Invalid date format. Use YYYY-MM-DD", "صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD"),
			}

		if booking_dt < getdate(nowdate()):
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"available": False,
				"message": _msg("Cannot book for past dates", "لا يمكن الحجز لتواريخ سابقة"),
			}

		# Check for conflicting bookings using ORM
		conflicting_bookings = frappe.get_all(
			"GRM Booking",
			filters={
				"space": space,
				"booking_date": booking_date,
				"status": ["in", ["Draft", "Confirmed", "Checked-in"]],
			},
			fields=["name", "start_time", "end_time", "status"],
		)

		# Filter overlaps in Python (safer than raw SQL)
		start_t = _parse_time_string(start_time)
		end_t = _parse_time_string(end_time)
		conflicts = []
		for b in conflicting_bookings:
			b_start = _parse_time_string(b.start_time)
			b_end = _parse_time_string(b.end_time)
			# Overlap: NOT (end <= b_start OR start >= b_end)
			if not (end_t <= b_start or start_t >= b_end):
				conflicts.append({
					"booking_id": b.name,
					"start_time": str(b.start_time),
					"end_time": str(b.end_time),
					"status": b.status,
				})

		if conflicts:
			frappe.response["http_status_code"] = 409
			return {
				"success": False,
				"http_status_code": 409,
				"available": False,
				"message": _msg("Space is already booked during this time", "المساحة محجوزة خلال هذا الوقت"),
				"conflicts": conflicts,
			}

		# Duration & pricing
		duration_hours = _calculate_duration_hours(start_time, end_time)

		if space_doc.min_booking_hours and duration_hours < space_doc.min_booking_hours:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"available": False,
				"message": _msg(
					f"Minimum booking duration is {space_doc.min_booking_hours} hours",
					f"الحد الأدنى لمدة الحجز هو {space_doc.min_booking_hours} ساعات",
				),
			}

		hourly_rate = flt(space_doc.hourly_rate)
		daily_rate = flt(space_doc.daily_rate)

		if duration_hours >= 8 and daily_rate > 0:
			estimated_price = daily_rate
			rate_type = "Daily"
		else:
			estimated_price = hourly_rate * duration_hours
			rate_type = "Hourly"

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"available": True,
			"message": _msg("Space is available", "المساحة متاحة"),
			"space_info": {
				"id": space_doc.name,
				"name": space_doc.space_name,
				"capacity": space_doc.capacity,
				"hourly_rate": hourly_rate,
				"daily_rate": daily_rate,
			},
			"booking_info": {
				"duration_hours": duration_hours,
				"rate_type": rate_type,
				"estimated_price": estimated_price,
			},
		}

	except frappe.ValidationError:
		frappe.response["http_status_code"] = 400
		return {
			"success": False,
			"http_status_code": 400,
			"message": _msg("Invalid input provided", "البيانات المدخلة غير صالحة"),
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist()
def create_booking(
	space=None,
	booking_date=None,
	start_time=None,
	end_time=None,
	booking_type="Hourly",
	attendees=1,
	purpose=None,
	notes=None,
):
	"""Create a new booking for the current logged-in user.

	Returns:
		201: Booking created
		400: Validation error
		401: Not authenticated
		404: Space not found / no tenant
		409: Space unavailable
		500: Server error
	"""
	try:
		auth_err = _require_auth()
		if auth_err:
			return auth_err

		# --- input validation ---
		space = _validate_docname(space)
		if not space or not booking_date or not start_time or not end_time:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("space, booking_date, start_time, and end_time are required", "المساحة وتاريخ الحجز ووقت البداية ووقت النهاية مطلوبون"),
			}

		purpose = _sanitize_text(purpose, 500)
		notes = _sanitize_text(notes, 1000)

		# Whitelist booking_type
		if booking_type not in ("Hourly", "Daily", "Multi-day"):
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("Invalid booking type", "نوع الحجز غير صالح"),
			}

		# Tenant
		tenant = _get_tenant_for_current_user()
		if not tenant:
			from grm_management.grm_management.user_events import ensure_tenant_exists
			result = ensure_tenant_exists()
			if result.get("success"):
				tenant = result.get("tenant")
			else:
				frappe.response["http_status_code"] = 404
				return {
					"success": False,
					"http_status_code": 404,
					"message": _msg("No tenant account found. Please contact support.", "لم يتم العثور على حساب مستأجر. يرجى التواصل مع الدعم."),
				}

		# Availability check
		availability = check_availability(space, booking_date, start_time, end_time)
		if not availability.get("success") or not availability.get("available"):
			return availability

		space_doc = frappe.get_doc("GRM Space", space)
		duration_hours = _calculate_duration_hours(start_time, end_time)

		attendees = cint(attendees) or 1
		if attendees > space_doc.capacity:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg(
					f"Number of attendees exceeds space capacity ({space_doc.capacity})",
					f"عدد الحضور يتجاوز سعة المساحة ({space_doc.capacity})",
				),
			}

		# Pricing
		hourly_rate = flt(space_doc.hourly_rate)
		daily_rate = flt(space_doc.daily_rate)

		if booking_type == "Daily" or (duration_hours >= 8 and daily_rate > 0):
			rate_type = "Daily"
			subtotal = daily_rate
		else:
			rate_type = "Hourly"
			subtotal = hourly_rate * duration_hours

		minimum_charge = flt(space_doc.minimum_charge)
		if minimum_charge > 0 and subtotal < minimum_charge:
			subtotal = minimum_charge

		# Create via Frappe ORM (respects hooks & validation)
		booking = frappe.new_doc("GRM Booking")
		booking.tenant = tenant
		booking.space = space
		booking.status = "Draft"
		booking.booking_type = booking_type
		booking.booking_date = booking_date
		booking.start_time = start_time
		booking.end_time = end_time
		booking.duration_hours = duration_hours
		booking.total_hours = duration_hours
		booking.attendees = attendees
		booking.purpose = purpose
		booking.rate_type = rate_type
		booking.hourly_rate = hourly_rate
		booking.subtotal = subtotal
		booking.total_amount = subtotal
		booking.notes = notes
		booking.payment_status = "Unpaid"
		booking.insert(ignore_permissions=True)
		frappe.db.commit()

		location_name = _get_space_location_name(space_doc.location)

		frappe.response["http_status_code"] = 201
		return {
			"success": True,
			"http_status_code": 201,
			"message": _msg("Booking created successfully", "تم إنشاء الحجز بنجاح"),
			"data": {
				"id": booking.name,
				"status": booking.status,
				"space": {
					"id": space_doc.name,
					"name": space_doc.space_name,
					"location": location_name,
				},
				"booking_date": str(booking.booking_date),
				"start_time": str(booking.start_time),
				"end_time": str(booking.end_time),
				"duration_hours": booking.duration_hours,
				"attendees": booking.attendees,
				"rate_type": booking.rate_type,
				"subtotal": booking.subtotal,
				"total_amount": booking.total_amount,
				"payment_status": booking.payment_status,
			},
		}

	except frappe.ValidationError:
		frappe.response["http_status_code"] = 400
		return {
			"success": False,
			"http_status_code": 400,
			"message": _msg("Invalid input provided", "البيانات المدخلة غير صالحة"),
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred while creating booking", "حدث خطأ غير متوقع أثناء إنشاء الحجز"),
		}


@frappe.whitelist()
def confirm_booking(booking_id=None):
	"""Confirm a draft booking.

	Returns:
		200: Booking confirmed
		400: Invalid status
		401: Not authenticated
		403: Not owner
		404: Booking not found
		409: Space no longer available
		500: Server error
	"""
	try:
		auth_err = _require_auth()
		if auth_err:
			return auth_err

		booking_id = _validate_docname(booking_id)
		if not booking_id:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("booking_id is required", "رقم الحجز مطلوب"),
			}

		if not frappe.db.exists("GRM Booking", booking_id):
			frappe.response["http_status_code"] = 404
			return {
				"success": False,
				"http_status_code": 404,
				"message": _msg("Booking not found", "الحجز غير موجود"),
			}

		tenant = _get_tenant_for_current_user()
		booking = frappe.get_doc("GRM Booking", booking_id)

		# Ownership check
		if booking.tenant != tenant and frappe.session.user != "Administrator":
			frappe.response["http_status_code"] = 403
			return {
				"success": False,
				"http_status_code": 403,
				"message": _msg("You do not have permission to confirm this booking", "ليس لديك صلاحية لتأكيد هذا الحجز"),
			}

		if booking.status != "Draft":
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("Only draft bookings can be confirmed", "يمكن تأكيد الحجوزات المسودة فقط"),
			}

		# Re-check availability
		availability = check_availability(
			booking.space,
			str(booking.booking_date),
			str(booking.start_time),
			str(booking.end_time),
		)

		if not availability.get("available"):
			# For non-conflict errors (space disabled, past date, etc.) return directly
			if not availability.get("conflicts"):
				return availability
			# For time conflicts, exclude the current booking itself
			conflicts = [c for c in availability.get("conflicts", []) if c.get("booking_id") != booking_id]
			if conflicts:
				frappe.response["http_status_code"] = 409
				return {
					"success": False,
					"http_status_code": 409,
					"message": _msg("Space is no longer available for this time slot", "المساحة لم تعد متاحة لهذا الوقت"),
					"conflicts": conflicts,
				}

		booking.status = "Confirmed"
		booking.save(ignore_permissions=True)
		frappe.db.commit()

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Booking confirmed successfully", "تم تأكيد الحجز بنجاح"),
			"data": {
				"booking_id": booking.name,
				"status": booking.status,
			},
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist()
def cancel_booking(booking_id=None, reason=None):
	"""Cancel a booking.

	Returns:
		200: Booking cancelled
		400: Invalid status
		401: Not authenticated
		403: Not owner
		404: Booking not found
		500: Server error
	"""
	try:
		auth_err = _require_auth()
		if auth_err:
			return auth_err

		booking_id = _validate_docname(booking_id)
		if not booking_id:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("booking_id is required", "رقم الحجز مطلوب"),
			}

		reason = _sanitize_text(reason, 500)

		if not frappe.db.exists("GRM Booking", booking_id):
			frappe.response["http_status_code"] = 404
			return {
				"success": False,
				"http_status_code": 404,
				"message": _msg("Booking not found", "الحجز غير موجود"),
			}

		tenant = _get_tenant_for_current_user()
		booking = frappe.get_doc("GRM Booking", booking_id)

		if booking.tenant != tenant and frappe.session.user != "Administrator":
			frappe.response["http_status_code"] = 403
			return {
				"success": False,
				"http_status_code": 403,
				"message": _msg("You do not have permission to cancel this booking", "ليس لديك صلاحية لإلغاء هذا الحجز"),
			}

		if booking.status in ("Checked-in", "Checked-out", "Cancelled"):
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("This booking cannot be cancelled in its current status", "لا يمكن إلغاء هذا الحجز في حالته الحالية"),
			}

		booking.status = "Cancelled"
		if reason:
			existing_notes = _sanitize_text(booking.notes, 2000) or ""
			booking.notes = f"{existing_notes}\n\nCancellation reason: {reason}".strip()
		booking.save(ignore_permissions=True)
		frappe.db.commit()

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Booking cancelled successfully", "تم إلغاء الحجز بنجاح"),
			"data": {
				"booking_id": booking.name,
				"status": booking.status,
			},
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist()
def get_my_bookings(status=None, from_date=None, to_date=None, limit=50):
	"""Get bookings for the current logged-in user.

	Returns:
		200: List of bookings
		401: Not authenticated
		500: Server error
	"""
	try:
		auth_err = _require_auth()
		if auth_err:
			return auth_err

		tenant = _get_tenant_for_current_user()
		if not tenant:
			frappe.response["http_status_code"] = 200
			return {
				"success": True,
				"http_status_code": 200,
				"message": _msg("No tenant account found", "لم يتم العثور على حساب مستأجر"),
				"data": {"bookings": [], "total": 0},
			}

		# Whitelist status values
		allowed_statuses = ("Draft", "Confirmed", "Checked-in", "Checked-out", "Cancelled")
		filters = {"tenant": tenant}

		if status:
			status = cstr(status).strip()
			if status not in allowed_statuses:
				frappe.response["http_status_code"] = 400
				return {
					"success": False,
					"http_status_code": 400,
					"message": _msg("Invalid status filter", "فلتر الحالة غير صالح"),
				}
			filters["status"] = status

		if from_date:
			try:
				getdate(from_date)
			except Exception:
				frappe.response["http_status_code"] = 400
				return {
					"success": False,
					"http_status_code": 400,
					"message": _msg("Invalid from_date format", "صيغة تاريخ البداية غير صحيحة"),
				}
			filters["booking_date"] = [">=", from_date]

		if to_date:
			try:
				getdate(to_date)
			except Exception:
				frappe.response["http_status_code"] = 400
				return {
					"success": False,
					"http_status_code": 400,
					"message": _msg("Invalid to_date format", "صيغة تاريخ النهاية غير صحيحة"),
				}
			if "booking_date" in filters and isinstance(filters["booking_date"], list):
				filters["booking_date"] = ["between", [from_date, to_date]]
			else:
				filters["booking_date"] = ["<=", to_date]

		# Cap limit to prevent abuse
		safe_limit = min(cint(limit) or 50, 100)

		bookings = frappe.get_all(
			"GRM Booking",
			filters=filters,
			fields=[
				"name", "space", "status", "booking_type",
				"booking_date", "start_time", "end_time",
				"duration_hours", "attendees", "purpose",
				"rate_type", "subtotal", "total_amount",
				"payment_status", "actual_check_in", "actual_check_out",
				"notes"
			],
			order_by="booking_date desc, start_time desc",
			limit_page_length=safe_limit,
		)

		result = []
		for booking in bookings:
			space_info = frappe.db.get_value(
				"GRM Space",
				booking.space,
				["space_name", "space_name_ar", "location", "space_image"],
				as_dict=True,
			)

			location_name = ""
			if space_info and space_info.location:
				location_name = _get_space_location_name(space_info.location)

			result.append({
				"id": booking.name,
				"status": booking.status,
				"booking_type": booking.booking_type,
				"space": {
					"id": booking.space,
					"name": space_info.space_name if space_info else booking.space,
					"name_ar": space_info.space_name_ar if space_info else "",
					"location": location_name,
					"image": get_full_image_url(space_info.space_image) if space_info else None,
				},
				"booking_date": str(booking.booking_date),
				"start_time": str(booking.start_time),
				"end_time": str(booking.end_time),
				"duration_hours": booking.duration_hours,
				"attendees": booking.attendees,
				"purpose": booking.purpose,
				"rate_type": booking.rate_type,
				"subtotal": booking.subtotal,
				"total_amount": booking.total_amount,
				"payment_status": booking.payment_status,
				"actual_check_in": str(booking.actual_check_in) if booking.actual_check_in else None,
				"actual_check_out": str(booking.actual_check_out) if booking.actual_check_out else None,
				"notes": booking.notes,
			})

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Bookings retrieved successfully", "تم استرجاع الحجوزات بنجاح"),
			"data": {"bookings": result, "total": len(result)},
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist()
def get_booking_details(booking_id=None):
	"""Get detailed information about a specific booking.

	Returns:
		200: Booking details
		401: Not authenticated
		403: Not owner
		404: Booking not found
		500: Server error
	"""
	try:
		auth_err = _require_auth()
		if auth_err:
			return auth_err

		booking_id = _validate_docname(booking_id)
		if not booking_id:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("booking_id is required", "رقم الحجز مطلوب"),
			}

		if not frappe.db.exists("GRM Booking", booking_id):
			frappe.response["http_status_code"] = 404
			return {
				"success": False,
				"http_status_code": 404,
				"message": _msg("Booking not found", "الحجز غير موجود"),
			}

		tenant = _get_tenant_for_current_user()
		booking = frappe.get_doc("GRM Booking", booking_id)

		if booking.tenant != tenant and frappe.session.user != "Administrator":
			frappe.response["http_status_code"] = 403
			return {
				"success": False,
				"http_status_code": 403,
				"message": _msg("You do not have permission to view this booking", "ليس لديك صلاحية لعرض هذا الحجز"),
			}

		space_doc = frappe.get_doc("GRM Space", booking.space)
		location_name = _get_space_location_name(space_doc.location)

		tenant_doc = frappe.get_doc("GRM Tenant", booking.tenant)

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Booking details retrieved successfully", "تم استرجاع تفاصيل الحجز بنجاح"),
			"data": {
				"id": booking.name,
				"status": booking.status,
				"booking_type": booking.booking_type,
				"tenant": {
					"id": tenant_doc.name,
					"name": tenant_doc.tenant_name,
					"email": tenant_doc.primary_email,
					"phone": tenant_doc.primary_phone,
				},
				"space": {
					"id": space_doc.name,
					"name": space_doc.space_name,
					"location": location_name,
					"capacity": space_doc.capacity,
					"image": get_full_image_url(space_doc.space_image),
				},
				"booking_date": str(booking.booking_date),
				"start_time": str(booking.start_time),
				"end_time": str(booking.end_time),
				"duration_hours": booking.duration_hours,
				"attendees": booking.attendees,
				"purpose": booking.purpose,
				"pricing": {
					"rate_type": booking.rate_type,
					"hourly_rate": booking.hourly_rate,
					"subtotal": booking.subtotal,
					"discount": booking.discount,
					"tax": booking.tax,
					"total_amount": booking.total_amount,
				},
				"payment_status": booking.payment_status,
				"invoice": booking.invoice,
				"check_in": {
					"actual_check_in": str(booking.actual_check_in) if booking.actual_check_in else None,
					"actual_check_out": str(booking.actual_check_out) if booking.actual_check_out else None,
					"overtime_hours": booking.overtime_hours,
					"overtime_charges": booking.overtime_charges,
				},
				"notes": booking.notes,
				"created_on": str(booking.creation),
				"modified_on": str(booking.modified),
			},
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist(allow_guest=True)
def get_available_slots(space=None, date=None, slot_duration_minutes=60):
	"""Get available time slots for a space on a specific date.

	Returns:
		200: Available time slots
		400: Validation error
		404: Space not found
		409: Space not bookable/available
		500: Server error
	"""
	try:
		space = _validate_docname(space)
		if not space or not date:
			frappe.response["http_status_code"] = 400
			return {
				"success": False,
				"http_status_code": 400,
				"message": _msg("space and date are required", "المساحة والتاريخ مطلوبان"),
			}

		if not frappe.db.exists("GRM Space", space):
			frappe.response["http_status_code"] = 404
			return {
				"success": False,
				"http_status_code": 404,
				"message": _msg("Space not found", "المساحة غير موجودة"),
			}

		space_doc = frappe.get_doc("GRM Space", space)

		if not space_doc.allow_booking:
			frappe.response["http_status_code"] = 409
			return {
				"success": False,
				"http_status_code": 409,
				"message": _msg("This space does not allow bookings", "هذه المساحة لا تقبل الحجوزات"),
				"data": {"slots": []},
			}

		if space_doc.status != "Available":
			frappe.response["http_status_code"] = 409
			return {
				"success": False,
				"http_status_code": 409,
				"message": _msg("Space is currently not available", "المساحة غير متاحة حالياً"),
				"data": {"slots": []},
			}

		working_start = 8
		working_end = 22
		# Cap slot duration to prevent abuse
		slot_duration = min(max(cint(slot_duration_minutes) or 60, 15), 480)

		# Use ORM instead of raw SQL
		existing_bookings = frappe.get_all(
			"GRM Booking",
			filters={
				"space": space,
				"booking_date": date,
				"status": ["in", ["Draft", "Confirmed", "Checked-in"]],
			},
			fields=["start_time", "end_time"],
		)

		booked_ranges = []
		for b in existing_bookings:
			b_start = _parse_time_string(b.start_time)
			b_end = _parse_time_string(b.end_time)
			booked_ranges.append((b_start.hour + b_start.minute / 60, b_end.hour + b_end.minute / 60))

		slots = []
		current_time = working_start
		while current_time + (slot_duration / 60) <= working_end:
			slot_end = current_time + (slot_duration / 60)

			is_available = True
			for booked_start, booked_end in booked_ranges:
				if not (slot_end <= booked_start or current_time >= booked_end):
					is_available = False
					break

			start_hour = int(current_time)
			start_minute = int((current_time - start_hour) * 60)
			end_hour = int(slot_end)
			end_minute = int((slot_end - end_hour) * 60)

			slots.append({
				"start_time": f"{start_hour:02d}:{start_minute:02d}",
				"end_time": f"{end_hour:02d}:{end_minute:02d}",
				"available": is_available,
				"duration_minutes": slot_duration,
			})

			current_time = slot_end

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Time slots retrieved successfully", "تم استرجاع الفترات الزمنية بنجاح"),
			"data": {
				"space": {"id": space_doc.name, "name": space_doc.space_name},
				"date": date,
				"slots": slots,
				"available_count": len([s for s in slots if s["available"]]),
				"total_slots": len(slots),
			},
		}

	except frappe.ValidationError:
		frappe.response["http_status_code"] = 400
		return {
			"success": False,
			"http_status_code": 400,
			"message": _msg("Invalid input provided", "البيانات المدخلة غير صالحة"),
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
		}


@frappe.whitelist()
def get_dashboard():
	"""Get dashboard summary data for the current logged-in user.

	Returns:
		200: Dashboard data
		401: Not authenticated
		500: Server error
	"""
	try:
		auth_err = _require_auth()
		if auth_err:
			return auth_err

		tenant = _get_tenant_for_current_user()

		empty_data = {
			"tenant": None,
			"customer": None,
			"subscriptions": [],
			"booking_stats": {
				"total_bookings": 0,
				"active_bookings": 0,
				"upcoming_bookings": 0,
				"completed_bookings": 0,
				"cancelled_bookings": 0,
				"total_spent": 0,
				"outstanding_amount": 0,
			},
			"upcoming": [],
			"recent": [],
		}

		if not tenant:
			frappe.response["http_status_code"] = 200
			return {
				"success": True,
				"http_status_code": 200,
				"message": _msg("No tenant account found", "لم يتم العثور على حساب مستأجر"),
				"data": empty_data,
			}

		today = nowdate()

		# 1) Tenant info
		tenant_doc = frappe.get_doc("GRM Tenant", tenant)
		tenant_data = {
			"tenant_id": tenant_doc.name,
			"tenant_name": tenant_doc.tenant_name,
			"tenant_type": tenant_doc.tenant_type,
			"status": tenant_doc.status,
			"primary_email": tenant_doc.primary_email,
			"primary_phone": tenant_doc.primary_phone,
			"city": tenant_doc.city,
			"address": tenant_doc.address_line1,
			"commercial_registration": tenant_doc.commercial_registration,
			"tax_id": tenant_doc.tax_id,
			"total_members": cint(tenant_doc.total_members),
			"active_subscriptions": cint(tenant_doc.active_subscriptions),
			"total_revenue": flt(tenant_doc.total_revenue),
			"total_outstanding": flt(tenant_doc.total_outstanding),
		}

		# 2) Customer financials (ORM-based)
		customer_data = None
		if tenant_doc.customer and frappe.db.exists("Customer", tenant_doc.customer):
			invoice_filters = {"customer": tenant_doc.customer, "docstatus": 1}

			total_invoiced = flt(frappe.db.get_value(
				"Sales Invoice", invoice_filters, "sum(grand_total)"
			))
			total_outstanding_inv = flt(frappe.db.get_value(
				"Sales Invoice", {**invoice_filters, "outstanding_amount": [">", 0]},
				"sum(outstanding_amount)",
			))
			total_paid = total_invoiced - total_outstanding_inv

			recent_invoices = frappe.get_all(
				"Sales Invoice",
				filters=invoice_filters,
				fields=["name", "posting_date", "grand_total", "outstanding_amount", "status"],
				order_by="posting_date desc",
				limit_page_length=5,
			)

			customer_data = {
				"customer_id": tenant_doc.customer,
				"total_invoiced": total_invoiced,
				"total_paid": total_paid,
				"total_outstanding": total_outstanding_inv,
				"recent_invoices": [
					{
						"id": inv.name,
						"date": str(inv.posting_date),
						"grand_total": flt(inv.grand_total),
						"outstanding": flt(inv.outstanding_amount),
						"status": inv.status,
					}
					for inv in recent_invoices
				],
			}

		# 3) Subscriptions (ORM)
		subscriptions_raw = frappe.get_all(
			"GRM Subscription",
			filters={"tenant": tenant},
			fields=[
				"name", "status", "subscription_type",
				"start_date", "end_date",
				"grand_total", "outstanding_amount",
				"total_entries_allowed", "entries_used", "remaining_entries",
				"auto_renew", "next_renewal_date",
			],
			order_by="start_date desc",
			limit_page_length=10,
		)

		subscriptions_list = []
		for sub in subscriptions_raw:
			subscriptions_list.append({
				"id": sub.name,
				"status": sub.status,
				"type": sub.subscription_type,
				"start_date": str(sub.start_date) if sub.start_date else None,
				"end_date": str(sub.end_date) if sub.end_date else None,
				"grand_total": flt(sub.grand_total),
				"outstanding": flt(sub.outstanding_amount),
				"entries": {
					"total": cint(sub.total_entries_allowed),
					"used": cint(sub.entries_used),
					"remaining": cint(sub.remaining_entries),
				} if sub.subscription_type == "Entry-based" else None,
				"auto_renew": bool(sub.auto_renew),
				"next_renewal_date": str(sub.next_renewal_date) if sub.next_renewal_date else None,
			})

		# 4) Booking stats (ORM)
		total_bookings = frappe.db.count("GRM Booking", {"tenant": tenant})
		active_bookings = frappe.db.count("GRM Booking", {
			"tenant": tenant, "status": ["in", ["Confirmed", "Checked-in"]],
		})
		upcoming_count = frappe.db.count("GRM Booking", {
			"tenant": tenant, "status": ["in", ["Draft", "Confirmed"]],
			"booking_date": [">=", today],
		})
		completed_bookings = frappe.db.count("GRM Booking", {
			"tenant": tenant, "status": "Checked-out",
		})
		cancelled_bookings = frappe.db.count("GRM Booking", {
			"tenant": tenant, "status": "Cancelled",
		})

		total_spent = flt(frappe.db.get_value(
			"GRM Booking",
			{"tenant": tenant, "status": ["in", ["Confirmed", "Checked-in", "Checked-out"]]},
			"sum(total_amount)",
		))
		outstanding_amount = flt(frappe.db.get_value(
			"GRM Booking",
			{
				"tenant": tenant,
				"payment_status": "Unpaid",
				"status": ["in", ["Confirmed", "Checked-in", "Checked-out"]],
			},
			"sum(total_amount)",
		))

		# 5) Upcoming bookings (next 5)
		upcoming_bookings = frappe.get_all(
			"GRM Booking",
			filters={
				"tenant": tenant,
				"status": ["in", ["Draft", "Confirmed"]],
				"booking_date": [">=", today],
			},
			fields=["name", "space", "status", "booking_date", "start_time", "end_time", "total_amount", "payment_status"],
			order_by="booking_date asc, start_time asc",
			limit_page_length=5,
		)

		upcoming_list = []
		for b in upcoming_bookings:
			space_info = frappe.db.get_value(
				"GRM Space", b.space,
				["space_name", "space_name_ar", "location", "space_image"],
				as_dict=True,
			)
			location_name = _get_space_location_name(space_info.location) if space_info and space_info.location else ""

			upcoming_list.append({
				"id": b.name,
				"status": b.status,
				"booking_date": str(b.booking_date),
				"start_time": str(b.start_time),
				"end_time": str(b.end_time),
				"total_amount": b.total_amount,
				"payment_status": b.payment_status,
				"space": {
					"id": b.space,
					"name": space_info.space_name if space_info else b.space,
					"name_ar": space_info.space_name_ar if space_info else "",
					"location": location_name,
					"image": get_full_image_url(space_info.space_image) if space_info else None,
				},
			})

		# 6) Recent bookings (last 5)
		recent_bookings = frappe.get_all(
			"GRM Booking",
			filters={"tenant": tenant, "status": ["in", ["Checked-out", "Cancelled"]]},
			fields=["name", "space", "status", "booking_date", "start_time", "end_time", "total_amount", "payment_status"],
			order_by="booking_date desc, start_time desc",
			limit_page_length=5,
		)

		recent_list = []
		for b in recent_bookings:
			space_info = frappe.db.get_value(
				"GRM Space", b.space,
				["space_name", "space_name_ar", "location"],
				as_dict=True,
			)
			location_name = _get_space_location_name(space_info.location) if space_info and space_info.location else ""

			recent_list.append({
				"id": b.name,
				"status": b.status,
				"booking_date": str(b.booking_date),
				"start_time": str(b.start_time),
				"end_time": str(b.end_time),
				"total_amount": b.total_amount,
				"payment_status": b.payment_status,
				"space": {
					"id": b.space,
					"name": space_info.space_name if space_info else b.space,
					"name_ar": space_info.space_name_ar if space_info else "",
					"location": location_name,
				},
			})

		frappe.response["http_status_code"] = 200
		return {
			"success": True,
			"http_status_code": 200,
			"message": _msg("Dashboard data retrieved successfully", "تم استرجاع بيانات لوحة التحكم بنجاح"),
			"data": {
				"tenant": tenant_data,
				"customer": customer_data,
				"subscriptions": subscriptions_list,
				"booking_stats": {
					"total_bookings": total_bookings,
					"active_bookings": active_bookings,
					"upcoming_bookings": upcoming_count,
					"completed_bookings": completed_bookings,
					"cancelled_bookings": cancelled_bookings,
					"total_spent": total_spent,
					"outstanding_amount": outstanding_amount,
				},
				"upcoming": upcoming_list,
				"recent": recent_list,
			},
		}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Booking API Error")
		frappe.response["http_status_code"] = 500
		return {
			"success": False,
			"http_status_code": 500,
			"message": _msg("An unexpected error occurred while loading dashboard", "حدث خطأ غير متوقع أثناء تحميل لوحة التحكم"),
		}
