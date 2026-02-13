import random

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address, cstr, strip_html


def _msg(en, ar):
    """Return bilingual message dict."""
    return {"en": en, "ar": ar}


def _sanitize_text(value, max_length=500):
    """Strip HTML tags and limit length to prevent XSS / abuse."""
    if not value:
        return None
    return cstr(strip_html(cstr(value)))[:max_length]


def _get_tenant_for_user(user=None):
    """Get the GRM Tenant linked to the given or current user."""
    if not user:
        user = frappe.session.user
    if user in ("Administrator", "Guest"):
        return None
    user_email = frappe.db.get_value("User", user, "email") or user
    return frappe.db.get_value("GRM Tenant", {"primary_email": user_email}, "name")


# ---------------------------------------------------------------------------
# Auth Status
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def auth_status():
    """
    Check whether the current request is authenticated
    and whether the user is a Website User or System User.
    """
    user = frappe.session.user
    is_authenticated = user != "Guest"

    user_type = None
    if is_authenticated:
        # Website User أو System User
        user_type = frappe.db.get_value("User", user, "user_type")

    frappe.response["http_status_code"] = 200
    return {
        "success": True,
        "http_status_code": 200,
        "message": (
            _msg("User is authenticated", "المستخدم مسجل الدخول")
            if is_authenticated
            else _msg("User is not authenticated", "المستخدم غير مسجل الدخول")
        ),
        "data": {
            "authenticated": is_authenticated,
            "user": user if is_authenticated else None,
            "is_website_user": user_type == "Website User" if is_authenticated else False,
            "user_type": user_type if is_authenticated else None,
        },
    }



# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def login(usr=None, pwd=None):
    """
    Log in a user with email and password.

    Args:
        usr: User email or username
        pwd: User password

    Returns:
        200: Login successful
        400: Missing credentials
        401: Invalid credentials
        500: Server error
    """
    try:
        if not usr or not pwd:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Email and password are required", "البريد الإلكتروني وكلمة المرور مطلوبان"),
            }

        frappe.local.login_manager.authenticate(usr, pwd)
        frappe.local.login_manager.post_login()

        user = frappe.session.user

        full_name, user_type = frappe.db.get_value(
            "User",
            user,
            ["full_name", "user_type"]
        )

        is_website_user = user_type == "Website User"

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("Login successful", "تم تسجيل الدخول بنجاح"),
            "data": {
                "user": user,
                "full_name": full_name,
            },
            "is_website_user": is_website_user,
        }

    except frappe.AuthenticationError:
        frappe.clear_messages()
        frappe.response["http_status_code"] = 401
        return {
            "success": False,
            "http_status_code": 401,
            "message": _msg("Invalid email or password", "البريد الإلكتروني أو كلمة المرور غير صحيحة"),
        }
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred. Please try again later.", "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقاً."),
        }


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
@frappe.whitelist()
def logout():
    """
    Log out the current user.

    Returns:
        200: Logout successful
        401: Not authenticated
        500: Server error
    """
    try:
        if frappe.session.user == "Guest":
            frappe.response["http_status_code"] = 401
            return {
                "success": False,
                "http_status_code": 401,
                "message": _msg("You are not logged in", "أنت غير مسجل الدخول"),
            }

        frappe.local.login_manager.logout()

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("Logged out successfully", "تم تسجيل الخروج بنجاح"),
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred during logout", "حدث خطأ غير متوقع أثناء تسجيل الخروج"),
        }


# ---------------------------------------------------------------------------
# Signup  (Guest → Website User + Tenant + Customer)
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
def signup(
    email=None,
    password=None,
    first_name=None,
    last_name=None,
    phone=None,
    tenant_type=None,
    company_name=None,
    commercial_registration=None,
    tax_id=None,
):
    """
    Register a new website user and create Tenant + Customer.

    For individuals: email, password, first_name are required.
    For companies:   additionally company_name is required;
                     commercial_registration (CR) and tax_id are optional.

    Returns:
        201: Signup successful
        400: Validation error
        409: Email already exists
        500: Server error
    """
    try:
        # --- validation -------------------------------------------------
        if not email or not password or not first_name:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Email, password, and first name are required", "البريد الإلكتروني وكلمة المرور والاسم الأول مطلوبون"),
            }

        # Sanitize text inputs
        first_name = _sanitize_text(first_name, 140)
        last_name = _sanitize_text(last_name, 140)
        phone = _sanitize_text(phone, 20)
        company_name = _sanitize_text(company_name, 255)
        commercial_registration = _sanitize_text(commercial_registration, 50)
        tax_id = _sanitize_text(tax_id, 50)

        email = cstr(email).strip().lower()

        if not validate_email_address(email):
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Invalid email address", "عنوان البريد الإلكتروني غير صالح"),
            }

        if len(password) < 4:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Password must be at least 4 characters", "كلمة المرور يجب أن تكون 4 أحرف على الأقل"),
            }

        tenant_type = tenant_type or "Individual"
        if tenant_type not in ("Individual", "Company"):
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Tenant type must be 'Individual' or 'Company'", "نوع المستأجر يجب أن يكون 'فرد' أو 'شركة'"),
            }

        if tenant_type == "Company" and not company_name:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Company name is required for company registration", "اسم الشركة مطلوب لتسجيل الشركات"),
            }

        # --- duplicate check --------------------------------------------
        if frappe.db.exists("User", email):
            frappe.response["http_status_code"] = 409
            return {
                "success": False,
                "http_status_code": 409,
                "message": _msg("An account with this email already exists", "يوجد حساب مسجل بهذا البريد الإلكتروني"),
            }

        # --- create Frappe user ------------------------------------------
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name

        user = frappe.new_doc("User")
        user.email = email
        user.first_name = first_name
        user.last_name = last_name or ""
        user.full_name = full_name
        user.mobile_no = phone or ""
        user.new_password = password
        user.enabled = 1
        user.user_type = "Website User"
        user.append("roles", {"role": "Customer"})
        # skip the on_user_update hook creating a tenant — we do it manually below
        user.flags.ignore_tenant_creation = True
        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.insert(ignore_permissions=True)

        # --- create GRM Tenant ------------------------------------------
        tenant_name_value = company_name if tenant_type == "Company" else full_name

        tenant = frappe.new_doc("GRM Tenant")
        tenant.tenant_name = tenant_name_value
        tenant.tenant_type = tenant_type
        tenant.status = "Active"
        tenant.primary_contact_person = full_name
        tenant.primary_email = email
        tenant.primary_phone = phone or ""
        if tenant_type == "Company":
            tenant.commercial_registration = commercial_registration or ""
            tenant.tax_id = tax_id or ""
        tenant.insert(ignore_permissions=True)
        # after_insert on Tenant auto-creates the ERPNext Customer

        frappe.db.commit()

        frappe.response["http_status_code"] = 201
        return {
            "success": True,
            "http_status_code": 201,
            "message": _msg("Account created successfully", "تم إنشاء الحساب بنجاح"),
            "data": {
                "user": user.name,
                "full_name": full_name,
                "tenant_id": tenant.name,
                "tenant_type": tenant_type,
            },
        }

    except frappe.ValidationError as e:
        frappe.db.rollback()
        frappe.response["http_status_code"] = 400
        return {
            "success": False,
            "http_status_code": 400,
            "message": _msg(
                cstr(e) or "Validation error during registration",
                cstr(e) or "خطأ في التحقق أثناء التسجيل",
            ),
        }

    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred during registration", "حدث خطأ غير متوقع أثناء التسجيل"),
        }


# ---------------------------------------------------------------------------
# Get Current User (profile)
# ---------------------------------------------------------------------------
@frappe.whitelist()
def get_current_user():
    """
    Get profile details of the authenticated user including tenant info.

    Returns:
        200: User profile + tenant data
        401: Not authenticated
        500: Server error
    """
    try:
        if frappe.session.user == "Guest":
            frappe.response["http_status_code"] = 401
            return {
                "success": False,
                "http_status_code": 401,
                "message": _msg("Authentication required", "يجب تسجيل الدخول"),
            }

        user = frappe.session.user
        user_doc = frappe.get_doc("User", user)

        # Tenant data
        tenant_data = None
        tenant_name = _get_tenant_for_user(user)
        if tenant_name:
            tenant = frappe.get_doc("GRM Tenant", tenant_name)
            tenant_data = {
                "tenant_id": tenant.name,
                "tenant_name": tenant.tenant_name,
                "tenant_type": tenant.tenant_type,
                "status": tenant.status,
                "phone": tenant.primary_phone,
                "company_name": tenant.tenant_name if tenant.tenant_type == "Company" else None,
                "commercial_registration": tenant.commercial_registration,
                "tax_id": tenant.tax_id,
                "city": tenant.city,
                "address": tenant.address_line1,
            }

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("User profile retrieved successfully", "تم استرجاع الملف الشخصي بنجاح"),
            "data": {
                "user": user_doc.name,
                "full_name": user_doc.full_name,
                "email": user_doc.email,
                "first_name": user_doc.first_name,
                "last_name": user_doc.last_name,
                "user_image": user_doc.user_image,
                "phone": user_doc.mobile_no,
                "roles": [role.role for role in user_doc.roles],
                "tenant": tenant_data,
                "gender": user_doc.gender,
                "date_of_birth": user_doc.birth_date,
                "username": user_doc.username,
            },
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred while fetching user profile", "حدث خطأ غير متوقع أثناء جلب الملف الشخصي"),
        }


# ---------------------------------------------------------------------------
# Update Profile
# ---------------------------------------------------------------------------
@frappe.whitelist()
def update_profile(
    first_name=None,
    last_name=None,
    phone=None,
    user_image=None,
    company_name=None,
    commercial_registration=None,
    tax_id=None,
    city=None,
    address=None,
):
    """
    Update profile info for the current user and their linked tenant.

    All params are optional — only provided fields are updated.

    Returns:
        200: Profile updated
        401: Not authenticated
        500: Server error
    """
    try:
        if frappe.session.user == "Guest":
            frappe.response["http_status_code"] = 401
            return {
                "success": False,
                "http_status_code": 401,
                "message": _msg("Authentication required", "يجب تسجيل الدخول"),
            }

        # Sanitize inputs
        first_name = _sanitize_text(first_name, 140) if first_name is not None else None
        last_name = _sanitize_text(last_name, 140) if last_name is not None else None
        phone = _sanitize_text(phone, 20) if phone is not None else None
        user_image = _sanitize_text(user_image, 500) if user_image is not None else None
        company_name = _sanitize_text(company_name, 255) if company_name is not None else None
        commercial_registration = _sanitize_text(commercial_registration, 50) if commercial_registration is not None else None
        tax_id = _sanitize_text(tax_id, 50) if tax_id is not None else None
        city = _sanitize_text(city, 100) if city is not None else None
        address = _sanitize_text(address, 255) if address is not None else None

        user = frappe.session.user
        user_doc = frappe.get_doc("User", user)

        # Update User fields
        if first_name is not None:
            user_doc.first_name = first_name
        if last_name is not None:
            user_doc.last_name = last_name
        if phone is not None:
            user_doc.mobile_no = phone
        if user_image is not None:
            user_doc.user_image = user_image

        user_doc.save(ignore_permissions=True)

        # Update Tenant fields
        tenant_name = _get_tenant_for_user(user)
        if tenant_name:
            tenant = frappe.get_doc("GRM Tenant", tenant_name)
            if phone is not None:
                tenant.primary_phone = phone
            # Sync tenant_name for Individual tenants when name changes
            if (first_name is not None or last_name is not None) and tenant.tenant_type == "Individual":
                tenant.tenant_name = user_doc.full_name
            if company_name is not None and tenant.tenant_type == "Company":
                tenant.tenant_name = company_name
            if commercial_registration is not None:
                tenant.commercial_registration = commercial_registration
            if tax_id is not None:
                tenant.tax_id = tax_id
            if city is not None:
                tenant.city = city
            if address is not None:
                tenant.address_line1 = address
            # keep contact person in sync
            full_name = user_doc.full_name
            tenant.primary_contact_person = full_name
            tenant.save(ignore_permissions=True)

            # --- Update linked Customer fields ---
            if tenant.customer and frappe.db.exists("Customer", tenant.customer):
                customer_doc = frappe.get_doc("Customer", tenant.customer)
                customer_changed = False

                # Sync customer_name from tenant_name
                if customer_doc.customer_name != tenant.tenant_name:
                    customer_doc.customer_name = tenant.tenant_name
                    customer_changed = True

                # Sync mobile_no from phone
                if phone is not None and customer_doc.mobile_no != phone:
                    customer_doc.mobile_no = phone
                    customer_changed = True

                # Sync image from user_image
                if user_image is not None and customer_doc.image != user_image:
                    customer_doc.image = user_image
                    customer_changed = True

                # Sync tax_id
                if tax_id is not None and customer_doc.tax_id != tenant.tax_id:
                    customer_doc.tax_id = tenant.tax_id
                    customer_changed = True

                if customer_changed:
                    customer_doc.save(ignore_permissions=True)

        frappe.db.commit()

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("Profile updated successfully", "تم تحديث الملف الشخصي بنجاح"),
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred while updating profile", "حدث خطأ غير متوقع أثناء تحديث الملف الشخصي"),
        }


# ---------------------------------------------------------------------------
# Change Password
# ---------------------------------------------------------------------------
@frappe.whitelist()
def change_password(current_password=None, new_password=None):
    """
    Change the password for the current user.

    Returns:
        200: Password changed
        400: Validation error
        401: Not authenticated / wrong current password
        500: Server error
    """
    try:
        if frappe.session.user == "Guest":
            frappe.response["http_status_code"] = 401
            return {
                "success": False,
                "http_status_code": 401,
                "message": _msg("Authentication required", "يجب تسجيل الدخول"),
            }

        if not current_password or not new_password:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Current password and new password are required", "كلمة المرور الحالية والجديدة مطلوبتان"),
            }

        if len(new_password) < 4:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("New password must be at least 4 characters", "كلمة المرور الجديدة يجب أن تكون 4 أحرف على الأقل"),
            }

        # Verify current password
        from frappe.utils.password import check_password
        try:
            check_password(frappe.session.user, current_password)
        except frappe.AuthenticationError:
            frappe.clear_messages()
            frappe.response["http_status_code"] = 401
            return {
                "success": False,
                "http_status_code": 401,
                "message": _msg("Current password is incorrect", "كلمة المرور الحالية غير صحيحة"),
            }

        # Update password
        from frappe.utils.password import update_password
        update_password(frappe.session.user, new_password)

        frappe.db.commit()

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("Password changed successfully", "تم تغيير كلمة المرور بنجاح"),
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred while changing password", "حدث خطأ غير متوقع أثناء تغيير كلمة المرور"),
        }


# ---------------------------------------------------------------------------
# Forgot Password  (send 6-digit code via email)
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
@rate_limit(key="email", limit=5, seconds=60 * 60)
def forgot_password(email=None):
    """
    Send a 6-digit verification code to the user's email for password reset.

    Always returns a generic success message to prevent user enumeration.

    Args:
        email: User email address

    Returns:
        200: Code sent (or generic success if email not found)
        400: Missing email
        500: Server error
    """
    try:
        if not email:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Email is required", "البريد الإلكتروني مطلوب"),
            }

        email = cstr(email).strip().lower()

        if not validate_email_address(email):
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Invalid email address", "عنوان البريد الإلكتروني غير صالح"),
            }

        # Generic success message (used regardless of whether user exists)
        success_resp = {
            "success": True,
            "http_status_code": 200,
            "message": _msg(
                "If an account with this email exists, a reset code has been sent",
                "إذا كان هناك حساب مرتبط بهذا البريد الإلكتروني، فقد تم إرسال رمز إعادة التعيين"
            ),
        }

        # Check user exists and is enabled — return generic success either way
        if not frappe.db.exists("User", email):
            frappe.response["http_status_code"] = 200
            return success_resp

        enabled = frappe.db.get_value("User", email, "enabled")
        if not enabled:
            frappe.response["http_status_code"] = 200
            return success_resp

        # Generate 6-digit code
        code = str(random.randint(100000, 999999))

        # Store in cache with 15-minute TTL
        cache_key = f"pwd_reset_code:{email}"
        frappe.cache.set_value(cache_key, {
            "code": code,
            "attempts": 0,
        }, expires_in_sec=15 * 60)

        # Get user first name for the email
        first_name = frappe.db.get_value("User", email, "first_name") or ""

        # Send bilingual email
        frappe.sendmail(
            recipients=email,
            subject="Password Reset Code | رمز إعادة تعيين كلمة المرور",
            message=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div dir="ltr">
                    <h2 style="color: #333;">Password Reset Code</h2>
                    <p>Hi {first_name},</p>
                    <p>You requested a password reset. Your verification code is:</p>
                    <div style="background: #f4f4f4; padding: 20px; text-align: center; font-size: 32px; letter-spacing: 8px; font-weight: bold; margin: 20px 0; border-radius: 8px; color: #333;">
                        {code}
                    </div>
                    <p>This code expires in <strong>15 minutes</strong>.</p>
                    <p style="color: #888;">If you did not request this, please ignore this email.</p>
                </div>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;" />
                <div dir="rtl" style="text-align: right;">
                    <h2 style="color: #333;">رمز إعادة تعيين كلمة المرور</h2>
                    <p>مرحباً {first_name}،</p>
                    <p>لقد طلبت إعادة تعيين كلمة المرور. رمز التحقق الخاص بك هو:</p>
                    <div style="background: #f4f4f4; padding: 20px; text-align: center; font-size: 32px; letter-spacing: 8px; font-weight: bold; margin: 20px 0; border-radius: 8px; color: #333;">
                        {code}
                    </div>
                    <p>ينتهي هذا الرمز خلال <strong>١٥ دقيقة</strong>.</p>
                    <p style="color: #888;">إذا لم تطلب هذا، يرجى تجاهل هذا البريد.</p>
                </div>
            </div>
            """,
            now=True,
        )

        frappe.response["http_status_code"] = 200
        return success_resp

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }


# ---------------------------------------------------------------------------
# Verify Reset Code  (validate code + set new password)
# ---------------------------------------------------------------------------
@frappe.whitelist(allow_guest=True)
@rate_limit(key="email", limit=10, seconds=60 * 60)
def verify_reset_code(email=None, code=None, new_password=None):
    """
    Verify the 6-digit code and reset the password.

    Args:
        email: User email address
        code: 6-digit verification code
        new_password: New password (min 4 chars)

    Returns:
        200: Password reset successful
        400: Validation / invalid code
        429: Too many attempts
        500: Server error
    """
    try:
        if not email or not code or not new_password:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg(
                    "Email, code, and new password are required",
                    "البريد الإلكتروني والرمز وكلمة المرور الجديدة مطلوبون"
                ),
            }

        email = cstr(email).strip().lower()

        if not validate_email_address(email):
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Invalid email address", "عنوان البريد الإلكتروني غير صالح"),
            }

        if len(new_password) < 4:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Password must be at least 4 characters", "كلمة المرور يجب أن تكون 4 أحرف على الأقل"),
            }

        # Retrieve stored code from cache
        cache_key = f"pwd_reset_code:{email}"
        stored = frappe.cache.get_value(cache_key)

        if not stored:
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg(
                    "Invalid or expired reset code. Please request a new one.",
                    "رمز إعادة التعيين غير صالح أو منتهي الصلاحية. يرجى طلب رمز جديد."
                ),
            }

        # Brute force protection: max 5 wrong attempts
        if stored.get("attempts", 0) >= 5:
            frappe.cache.delete_value(cache_key)
            frappe.response["http_status_code"] = 429
            return {
                "success": False,
                "http_status_code": 429,
                "message": _msg(
                    "Too many invalid attempts. Please request a new reset code.",
                    "عدد كبير من المحاولات الخاطئة. يرجى طلب رمز إعادة تعيين جديد."
                ),
            }

        # Compare codes
        if cstr(code).strip() != stored["code"]:
            stored["attempts"] = stored.get("attempts", 0) + 1
            frappe.cache.set_value(cache_key, stored, expires_in_sec=15 * 60)
            frappe.response["http_status_code"] = 400
            return {
                "success": False,
                "http_status_code": 400,
                "message": _msg("Invalid reset code", "رمز إعادة التعيين غير صحيح"),
            }

        # Code matches — verify user exists
        if not frappe.db.exists("User", email):
            frappe.cache.delete_value(cache_key)
            frappe.response["http_status_code"] = 404
            return {
                "success": False,
                "http_status_code": 404,
                "message": _msg("User not found", "المستخدم غير موجود"),
            }

        # Update password (low-level, no policy check)
        from frappe.utils.password import update_password
        update_password(email, new_password)

        # Delete code to prevent reuse
        frappe.cache.delete_value(cache_key)

        frappe.db.commit()

        frappe.response["http_status_code"] = 200
        return {
            "success": True,
            "http_status_code": 200,
            "message": _msg("Password has been reset successfully", "تم إعادة تعيين كلمة المرور بنجاح"),
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auth API Error")
        frappe.response["http_status_code"] = 500
        return {
            "success": False,
            "http_status_code": 500,
            "message": _msg("An unexpected error occurred", "حدث خطأ غير متوقع"),
        }
