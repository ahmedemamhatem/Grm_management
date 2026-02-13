# Copyright (c) 2026, Wael ELsafty and contributors
# For license information, please see license.txt

import frappe


def _msg(en, ar):
    """Return bilingual message dict."""
    return {"en": en, "ar": ar}


def _split_lines(text):
    """Split a newline-separated text field into a list, filtering empty lines."""
    if not text:
        return []
    return [line.strip() for line in text.split("\n") if line.strip()]


# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_home_page():
    """Get all Home Page content for the website.

    Returns:
        200: Full home page data (hero, about, features, workflow, pricing, testimonials, faqs)
        500: Server error
    """
    try:
        doc = frappe.get_single("GRM Home Page")

        data = {
            "hero": {
                "customer_rate": doc.customer_rate,
                "heading_1": doc.heading_1,
                "heading_2": doc.heading_2,
                "heading_3": doc.heading_3,
                "paragraph": doc.paragraph,
                "hero_img": doc.hero_img,
            },
            "about": {
                "experience": doc.experience,
                "title": doc.about_title,
                "description": doc.about_description,
                "about_img": doc.about_img,
            },
            "features": [
                {"feature_icon": f.feature_icon, "title": f.title}
                for f in (doc.features or [])
            ],
            "workflow": {
                "title": doc.workflow_title,
                "description": doc.workflow_description,
                "workflow_img": doc.workflow_img,
                "items": [
                    {
                        "title": w.title,
                        "points": _split_lines(w.points),
                    }
                    for w in (doc.workflows or [])
                ],
            },
            "pricing": {
                "title": doc.pricing_title,
                "plans": [
                    {
                        "title": p.title,
                        "price": p.price,
                        "description": p.description,
                        "features": _split_lines(p.plan_features),
                    }
                    for p in (doc.plans or [])
                ],
            },
            "testimonials": {
                "title": doc.testimonials_title,
                "img": doc.testimonials_img,
                "items": [
                    {
                        "name": t.test_name,
                        "img": t.test_img,
                        "rate": t.test_rate,
                        "description": t.test_description,
                    }
                    for t in (doc.testimonials or [])
                ],
            },
            "faqs": [
                {"question": f.question, "answer": f.answer}
                for f in (doc.faqs or [])
            ],
        }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "Home page data retrieved successfully",
                "تم جلب بيانات الصفحة الرئيسية بنجاح",
            ),
            "data": data,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - Home Page")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# About Page
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_about_page():
    """Get all About Page content for the website.

    Returns:
        200: About page data (about section, features, services)
        500: Server error
    """
    try:
        doc = frappe.get_single("GRM About Page")

        data = {
            "about": {
                "title": doc.title,
                "description": doc.description,
                "features": _split_lines(doc.features),
            },
            "services": {
                "title": doc.services_title,
                "description": doc.services_description,
                "img": doc.service_img,
                "items": [
                    {
                        "title": s.title,
                        "description": s.description,
                        "img": s.img,
                    }
                    for s in (doc.services or [])
                ],
            },
        }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "About page data retrieved successfully",
                "تم جلب بيانات صفحة من نحن بنجاح",
            ),
            "data": data,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - About Page")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# Clients Page
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_clients_page():
    """Get all Clients Page content for the website.

    Returns:
        200: Clients page data (list of clients)
        500: Server error
    """
    try:
        doc = frappe.get_single("GRM Clients Page")

        data = {
            "clients": [
                {
                    "img": c.client_img,
                    "title": c.client_title,
                    "url": c.client_url,
                }
                for c in (doc.clients or [])
            ],
        }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "Clients page data retrieved successfully",
                "تم جلب بيانات صفحة العملاء بنجاح",
            ),
            "data": data,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - Clients Page")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# Why GRM Page
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_why_page():
    """Get all Why GRM Page content for the website.

    Returns:
        200: Why GRM page data (why section, tabs)
        500: Server error
    """
    try:
        doc = frappe.get_single("GRM Why Page")

        data = {
            "why": {
                "title": doc.title,
                "description": doc.description,
                "img": doc.img,
                "img_badge": doc.img_badge,
                "img_description": doc.img_description,
            },
            "tabs": [
                {
                    "tab_title": t.tab_title,
                    "tab_rate": t.tab_rate,
                    "tab_description": t.tab_description,
                    "points": _split_lines(t.points),
                }
                for t in (doc.tabs or [])
            ],
        }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "Why GRM page data retrieved successfully",
                "تم جلب بيانات صفحة لماذا GRM بنجاح",
            ),
            "data": data,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - Why Page")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# Contact Page
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_contact_page():
    """Get all Contact Page content for the website.

    Returns:
        200: Contact page data (title, social links, branches)
        500: Server error
    """
    try:
        doc = frappe.get_single("GRM Contact Page")

        data = {
            "title": doc.title,
            "social_links": [
                {
                    "platform": s.platform,
                    "url": s.url,
                    "icon": s.icon,
                }
                for s in (doc.social_media_links or [])
            ],
            "branches": [
                {
                    "title": b.title,
                    "description": b.description,
                    "email": b.email,
                    "phone": b.phone,
                    "location": b.location,
                }
                for b in (doc.branches or [])
            ],
        }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "Contact page data retrieved successfully",
                "تم جلب بيانات صفحة التواصل بنجاح",
            ),
            "data": data,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - Contact Page")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# Spaces (with all pricing)
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_spaces():
    """Get all available spaces with full pricing for the website.

    Args:
        space_type: (optional) Filter by GRM Space Type name
        location: (optional) Filter by GRM Location name

    Returns:
        200: Spaces grouped by type with all pricing tiers
        500: Server error
    """
    try:
        space_type = frappe.form_dict.get("space_type")
        location = frappe.form_dict.get("location")

        filters = {"status": "Available"}
        if space_type:
            filters["space_type"] = space_type
        if location:
            filters["location"] = location

        spaces = frappe.get_all(
            "GRM Space",
            filters=filters,
            fields=[
                "name", "space_name", "space_name_ar", "space_code",
                "space_type", "location", "property", "status",
                "area_sqm", "capacity", "min_booking_hours",
                "floor_number", "room_number",
                "is_featured", "allow_booking",
                "hourly_rate", "daily_rate", "monthly_rate", "annual_rate",
                "minimum_charge",
                "wifi", "air_conditioning", "projector", "whiteboard",
                "coffee_tea", "parking", "printer_access", "phone_line",
                "custom_amenities",
                "description", "space_image",
            ],
            order_by="is_featured desc, space_name asc",
        )

        # Get space type info for grouping
        space_types = {}
        if spaces:
            type_names = list({s.space_type for s in spaces if s.space_type})
            if type_names:
                types = frappe.get_all(
                    "GRM Space Type",
                    filters={"name": ["in", type_names]},
                    fields=[
                        "name", "space_type_name", "space_type_name_ar",
                        "category", "icon", "color_code",
                        "description", "typical_usage",
                        "hourly_rate", "daily_rate", "monthly_rate", "annual_rate",
                    ],
                )
                space_types = {t.name: t for t in types}

        # Get location Arabic names
        location_names = {}
        if spaces:
            loc_ids = list({s.location for s in spaces if s.location})
            if loc_ids:
                locs = frappe.get_all(
                    "GRM Location",
                    filters={"name": ["in", loc_ids]},
                    fields=["name", "location_name_ar"],
                )
                location_names = {l.name: l.location_name_ar for l in locs}

        # Build amenities list from boolean fields
        amenity_fields = [
            ("wifi", "WiFi"),
            ("air_conditioning", "Air Conditioning"),
            ("projector", "Projector"),
            ("whiteboard", "Whiteboard"),
            ("coffee_tea", "Coffee & Tea"),
            ("parking", "Parking"),
            ("printer_access", "Printer Access"),
            ("phone_line", "Phone Line"),
        ]

        # Group by space type
        grouped = {}
        for s in spaces:
            amenities = [label for field, label in amenity_fields if s.get(field)]

            st = space_types.get(s.space_type, {})

            space_data = {
                "id": s.name,
                "space_name": s.space_name,
                "space_name_ar": s.space_name_ar,
                "space_code": s.space_code,
                "location": s.location,
                "location_ar": location_names.get(s.location, ""),
                "property": s.property,
                "status": s.status,
                "area_sqm": s.area_sqm,
                "capacity": s.capacity,
                "min_booking_hours": s.min_booking_hours,
                "floor_number": s.floor_number,
                "room_number": s.room_number,
                "is_featured": s.is_featured,
                "allow_booking": s.allow_booking,
                "pricing": {
                    "hourly_rate": s.hourly_rate or 0,
                    "daily_rate": s.daily_rate or 0,
                    "monthly_rate": s.monthly_rate or 0,
                    "annual_rate": s.annual_rate or 0,
                    "minimum_charge": s.minimum_charge or 0,
                },
                "amenities": amenities,
                "custom_amenities": s.custom_amenities,
                "description": s.description,
                "space_image": s.space_image,
            }

            type_key = s.space_type or "Other"
            if type_key not in grouped:
                grouped[type_key] = {
                    "type_info": {
                        "name": st.get("space_type_name", s.space_type),
                        "name_ar": st.get("space_type_name_ar", ""),
                        "category": st.get("category", ""),
                        "icon": st.get("icon", ""),
                        "color": st.get("color_code", ""),
                        "description": st.get("description", ""),
                        "typical_usage": st.get("typical_usage", ""),
                        "default_pricing": {
                            "hourly_rate": st.get("hourly_rate", 0) or 0,
                            "daily_rate": st.get("daily_rate", 0) or 0,
                            "monthly_rate": st.get("monthly_rate", 0) or 0,
                            "annual_rate": st.get("annual_rate", 0) or 0,
                        },
                    },
                    "spaces": [],
                    "count": 0,
                }
            grouped[type_key]["spaces"].append(space_data)
            grouped[type_key]["count"] += 1

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "Spaces retrieved successfully",
                "تم جلب المساحات بنجاح",
            ),
            "data": grouped,
            "total_spaces": len(spaces),
            "total_types": len(grouped),
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - Spaces")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# All Pages (single call)
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def get_all_pages():
    """Get content for all website pages in a single call.

    Useful for SSR or preloading all CMS content at once.

    Returns:
        200: Dict with all page data keyed by page name
        500: Server error
    """
    try:
        result = {}

        # Collect each page, catching individual failures gracefully
        page_getters = {
            "home": get_home_page,
            "about": get_about_page,
            "clients": get_clients_page,
            "why_grm": get_why_page,
            "contact": get_contact_page,
            "spaces": get_spaces,
        }

        for page_name, getter in page_getters.items():
            try:
                response = getter()
                if response.get("success"):
                    result[page_name] = response.get("data")
                else:
                    result[page_name] = None
            except Exception:
                result[page_name] = None

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "All page data retrieved successfully",
                "تم جلب بيانات جميع الصفحات بنجاح",
            ),
            "data": result,
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Website API Error - All Pages")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }
