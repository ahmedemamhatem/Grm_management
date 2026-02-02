# GRM Management - Complete Test Guide & Documentation

## Table of Contents
1. [Module Overview](#module-overview)
2. [System Architecture](#system-architecture)
3. [Complete Workflow](#complete-workflow)
4. [Test Cases A-Z](#test-cases-a-z)
5. [API Testing](#api-testing)
6. [Automated Tasks](#automated-tasks)

---

## Module Overview

**GRM Management** is a comprehensive Coworking Space Management System built on Frappe/ERPNext v15+ that manages:

- **Members & Customers**: Individual and corporate clients
- **Spaces & Locations**: Physical spaces, rooms, desks across multiple locations
- **Contracts & Memberships**: Long-term rentals and flexible membership packages
- **Bookings**: Hourly, daily, and multi-day space reservations
- **Access Control**: Biometric device integration (ZK + BioTime API)
- **Financial Tracking**: Automated invoicing, payments, and expense management

---

## System Architecture

### Core Modules

```
┌─────────────────────────────────────────────────────────────┐
│                    GRM Management System                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Members    │───▶│  Contracts   │───▶│   Invoices   │ │
│  │ (Customers)  │    │ (Long-term)  │    │  (ERPNext)   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                     │                    ▲        │
│         │                     ▼                    │        │
│         │            ┌──────────────┐              │        │
│         │            │    Spaces    │              │        │
│         │            │  & Locations │              │        │
│         │            └──────────────┘              │        │
│         │                     │                    │        │
│         ▼                     ▼                    │        │
│  ┌──────────────┐    ┌──────────────┐    ┌────────┴─────┐ │
│  │ Memberships  │    │   Bookings   │───▶│   Payments   │ │
│  │  (Packages)  │    │ (Short-term) │    │  (ERPNext)   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                     │                             │
│         └─────────┬───────────┘                             │
│                   ▼                                         │
│           ┌──────────────┐                                  │
│           │ Access Rules │                                  │
│           │ & Devices    │                                  │
│           └──────────────┘                                  │
│                   │                                         │
│                   ▼                                         │
│           ┌──────────────┐                                  │
│           │ Access Logs  │                                  │
│           │  (History)   │                                  │
│           └──────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Setup Phase**: Create Locations → Space Types → Spaces
2. **Member Onboarding**: Create Member → Auto-create ERPNext Customer → Generate ZK User ID
3. **Contract Flow**: Create Contract → Approve → Occupy Spaces → Create Access Rules → Generate Invoice
4. **Membership Flow**: Create Membership → Activate → Grant Access → Track Usage
5. **Booking Flow**: Check Availability → Create Booking → Confirm → Check-in → Grant Temporary Access → Check-out
6. **Access Control**: Sync Devices → Monitor Access Logs → Auto-expire access
7. **Financial Flow**: Auto-generate Invoices → Track Payments → Manage Expenses

---

## Complete Workflow

### Phase 1: System Setup

#### 1.1 Create GRM Locations
**Purpose**: Define physical locations/branches

```python
location = frappe.new_doc("GRM Location")
location.location_name = "Downtown Coworking Hub"
location.location_code = "DT-001"
location.status = "Active"
location.email = "downtown@cowork.com"
location.phone = "+966-11-2345678"
location.address_line_1 = "123 King Fahd Road"
location.city = "Riyadh"
location.state = "Riyadh Province"
location.postal_code = "11564"
location.country = "Saudi Arabia"
location.rent_cost = 50000
location.utilities_cost = 8000
location.maintenance_cost = 5000
location.staff_cost = 25000
location.insert()
```

**Expected Result**:
- ✓ Location created with code DT-001
- ✓ Total monthly costs auto-calculated: 88,000 SAR

#### 1.2 Create Space Types
**Purpose**: Define categories of spaces with pricing

```python
space_type = frappe.new_doc("Space Type")
space_type.type_name = "Private Office"
space_type.type_code = "PO"
space_type.default_capacity = 4
space_type.allow_hourly = 0
space_type.allow_daily = 1
space_type.allow_monthly = 1
space_type.allow_long_term = 1
space_type.daily_rate = 500
space_type.monthly_rate = 10000
space_type.insert()
```

**Expected Result**:
- ✓ Space Type created: PO
- ✓ Available for daily and monthly bookings
- ✓ Pricing: 500 SAR/day, 10,000 SAR/month

#### 1.3 Create Spaces
**Purpose**: Create individual bookable spaces

```python
space = frappe.new_doc("Space")
space.space_name = "Executive Office A-101"
space.space_code = "DT-A101"
space.location = "DT-001"  # Downtown location
space.space_type = "PO"     # Private Office
space.capacity = 4
space.area_sqm = 25
space.floor = "1st Floor"
space.status = "Available"
space.use_custom_pricing = 0  # Use space type pricing
space.insert()
```

**Expected Result**:
- ✓ Space created: DT-A101
- ✓ Status: Available
- ✓ Location statistics updated (total_spaces +1)

### Phase 2: Member Management

#### 2.1 Create Individual Member
**Purpose**: Register a new member/client

```python
member = frappe.new_doc("Member")
member.member_name = "Ahmed Al-Rashid"
member.member_code = "MEM-001"
member.member_type = "Individual"
member.primary_email = "ahmed.rashid@email.com"
member.primary_mobile = "+966-50-1234567"
member.join_date = "2026-01-21"
member.status = "Active"
member.id_type = "National ID"
member.idcr_number = "1234567890"
member.insert()
```

**Auto-Generated**:
- ✓ ERPNext Customer created: "Ahmed Al-Rashid"
- ✓ ZK User ID generated: "1001"
- ✓ Member Code: MEM-001 (document name)

#### 2.2 Create Company Member
**Purpose**: Register corporate client

```python
member = frappe.new_doc("Member")
member.member_name = "TechStart Solutions"
member.member_code = "MEM-002"
member.member_type = "Company"
member.primary_email = "info@techstart.com"
member.primary_mobile = "+966-50-9876543"
member.join_date = "2026-01-21"
member.status = "Active"
member.id_type = "CR"
member.idcr_number = "7654321098"
member.tax_id = "300123456700003"
member.insert()
```

**Auto-Generated**:
- ✓ ERPNext Customer (Company): "TechStart Solutions"
- ✓ ZK User ID: "1002"

### Phase 3: Contract Management (Long-term Rental)

#### 3.1 Create Draft Contract
**Purpose**: Create space rental agreement

```python
contract = frappe.new_doc("GRM Contract")
contract.member = "MEM-001"  # Ahmed Al-Rashid
contract.contract_type = "Space Rental"
contract.status = "Draft"
contract.start_date = "2026-02-01"
contract.end_date = "2026-08-01"  # 6 months
contract.monthly_rent = 10000
contract.security_deposit = 10000
contract.notice_period_days = 30
contract.auto_renew = 0

# Add space to contract
contract.append("spaces", {
    "space": "DT-A101",
    "monthly_rent": 10000
})

# Add authorized user (member can grant access to team members)
contract.append("granted_users", {
    "user_name": "Ahmed Al-Rashid",
    "email": "ahmed.rashid@email.com",
    "access_granted": 1
})

contract.insert()
```

**Expected Result**:
- ✓ Contract created in Draft status
- ✓ Contract Number: CTR-2026-00001
- ✓ Duration calculated: 6 months
- ✓ Space DT-A101 linked

#### 3.2 Approve Contract
**Purpose**: Activate contract and grant access

```python
contract = frappe.get_doc("GRM Contract", "CTR-2026-00001")
contract.approve()
```

**What Happens**:
1. ✓ Contract status → "Active"
2. ✓ Space DT-A101 status → "Occupied"
3. ✓ Space.current_member → "MEM-001"
4. ✓ Access Rule created for Ahmed
5. ✓ Access Rule synced to devices
6. ✓ Sales Invoice created (First month: 10,000 + 10,000 deposit = 20,000 SAR)
7. ✓ Member statistics updated

**Verify**:
```python
# Check space status
space = frappe.get_doc("Space", "DT-A101")
print(f"Space Status: {space.status}")  # Occupied
print(f"Current Member: {space.current_member}")  # MEM-001

# Check access rule
access_rule = frappe.get_last_doc("Access Rule", filters={"member": "MEM-001"})
print(f"Access Status: {access_rule.status}")  # Active

# Check invoice
invoice = frappe.get_last_doc("Sales Invoice", filters={"customer": "Ahmed Al-Rashid"})
print(f"Invoice Total: {invoice.grand_total}")  # 20,000 SAR
```

### Phase 4: Membership Management (Flexible Packages)

#### 4.1 Create Membership Package (Using ERPNext Package)
**Note**: Using ERPNext's Package DocType with custom fields

```python
package = frappe.new_doc("Package")
package.package_name = "Flexi Desk - 10 Days"
package.package_type = "Membership"
package.validity_days = 30
package.price = 2500
# Custom fields
package.access_type = "Shared Desk"
package.access_limit = 10
package.access_24_7 = 0
package.access_start_time = "08:00:00"
package.access_end_time = "18:00:00"
package.insert()
```

#### 4.2 Create Membership
**Purpose**: Sell package to member

```python
membership = frappe.new_doc("Membership")
membership.member = "MEM-002"  # TechStart Solutions
membership.package = "Flexi Desk - 10 Days"
membership.status = "Draft"
membership.start_date = "2026-02-01"
membership.end_date = "2026-03-02"  # 30 days
membership.package_price = 2500
membership.discount_percent = 10
membership.insert()

# Activate membership
membership = frappe.get_doc("Membership", membership.name)
membership.activate()
```

**What Happens**:
1. ✓ Membership status → "Active"
2. ✓ Discount applied: 2500 - 10% = 2,250 SAR
3. ✓ Access Rule created
4. ✓ Access counters initialized: total_access_allowed = 10, access_used = 0
5. ✓ Sales Invoice created: 2,250 SAR

**Usage Tracking**:
```python
# Member uses access (via booking check-in)
membership.decrement_access(1)  # access_used = 1, remaining = 9
```

### Phase 5: Booking Management (Short-term)

#### 5.1 Check Space Availability
**Purpose**: Verify space is free before booking

```python
from grm_management.grm_management.api import check_space_availability

result = check_space_availability(
    space="DT-A101",
    date="2026-02-15",
    start_time="09:00:00",
    end_time="17:00:00"
)
print(result)
```

**Expected Response**:
```json
{
  "available": false,
  "message": "Space is occupied by contract CTR-2026-00001"
}
```

Let's try another space:
```python
# Create hot desk space first
hotdesk = frappe.new_doc("Space")
hotdesk.space_name = "Hot Desk HD-05"
hotdesk.space_code = "DT-HD05"
hotdesk.location = "DT-001"
hotdesk.space_type = "HD"  # Assuming Hot Desk type exists
hotdesk.capacity = 1
hotdesk.status = "Available"
hotdesk.insert()

# Check availability
result = check_space_availability(
    space="DT-HD05",
    date="2026-02-15",
    start_time="09:00:00",
    end_time="17:00:00"
)
```

**Expected Response**:
```json
{
  "available": true,
  "space": "DT-HD05",
  "date": "2026-02-15"
}
```

#### 5.2 Create Booking
**Purpose**: Reserve space for specific date/time

```python
booking = frappe.new_doc("Booking")
booking.member = "MEM-002"
booking.booking_type = "Daily"
booking.status = "Draft"
booking.source = "Online"
booking.space = "DT-HD05"
booking.booking_date = "2026-02-15"
booking.start_time = "09:00:00"
booking.end_time = "17:00:00"
booking.rate_type = "Daily Rate"
booking.insert()
```

**Auto-Calculated**:
- ✓ Location fetched from space
- ✓ Duration calculated: 8 hours
- ✓ Booking Number: BKG-2026-00001

#### 5.3 Confirm Booking
**Purpose**: Finalize reservation and create invoice

```python
booking = frappe.get_doc("Booking", "BKG-2026-00001")
booking.confirm()
```

**What Happens**:
1. ✓ Booking status → "Confirmed"
2. ✓ Space reserved for date/time
3. ✓ Sales Invoice created
4. ✓ Email confirmation sent (if configured)

#### 5.4 Check-in
**Purpose**: Member arrives and access is granted

```python
booking = frappe.get_doc("Booking", "BKG-2026-00001")
booking.check_in()
```

**What Happens**:
1. ✓ Booking status → "Checked-In"
2. ✓ actual_check_in timestamp recorded
3. ✓ Temporary Access Rule created (valid for booking duration)
4. ✓ Access granted to devices
5. ✓ Access Log created (Check-In event)
6. ✓ If using membership: access counter decremented

#### 5.5 Check-out
**Purpose**: Member leaves, calculate overtime

```python
booking = frappe.get_doc("Booking", "BKG-2026-00001")
booking.check_out()
```

**What Happens**:
1. ✓ Booking status → "Completed"
2. ✓ actual_check_out timestamp recorded
3. ✓ Overtime calculated (if late)
4. ✓ Additional charges added
5. ✓ Temporary Access Rule deactivated
6. ✓ Access removed from devices

**Overtime Example**:
```python
# Booking end time: 17:00:00
# Actual check-out: 18:30:00
# Overtime: 1.5 hours
# Overtime charge: 1.5 × hourly_rate × 1.5 (penalty)
```

### Phase 6: Access Control

#### 6.1 Setup Access Device - Direct ZK Mode

```python
device = frappe.new_doc("Access Device")
device.device_name = "Main Entrance Fingerprint"
device.device_code = "ZK-DT-001"
device.device_type = "Fingerprint"
device.location = "DT-001"
device.connection_mode = "Direct ZK"
device.ip_address = "192.168.1.100"
device.port = 4370
device.status = "Offline"
device.auto_sync = 1
device.insert()
```

**Test Connection**:
```python
device = frappe.get_doc("Access Device", "ZK-DT-001")
result = device.test_connection()
```

**Expected Result** (if device accessible):
```json
{
  "status": "success",
  "message": "Connected successfully",
  "device_info": {
    "serial_number": "DFA12345",
    "firmware": "Ver 6.60",
    "users": 150
  }
}
```

#### 6.2 Setup BioTime API Mode

```python
biotime = frappe.get_doc("BioTime Settings", "BioTime Settings")
biotime.enabled = 1
biotime.server_url = "192.168.1.10"
biotime.port = 8000
biotime.username = "admin"
biotime.set_value("password", "biotime123")
biotime.auto_sync = 1
biotime.sync_interval_minutes = 60
biotime.save()

# Test connection
result = biotime.test_connection()
```

**Create BioTime Device**:
```python
device = frappe.new_doc("Access Device")
device.device_name = "BioTime Main Door"
device.device_code = "BIO-DT-001"
device.device_type = "Fingerprint"
device.location = "DT-001"
device.connection_mode = "BioTime API"
device.use_biotime = 1
device.biotime_device_serial = "DGF9876543"
device.status = "Online"
device.auto_sync = 1
device.insert()
```

#### 6.3 Sync Access to Devices

```python
# Get active access rule
access_rule = frappe.get_last_doc("Access Rule", filters={
    "member": "MEM-001",
    "status": "Active"
})

# Sync to all devices
access_rule.sync_to_devices()
```

**What Happens**:
1. ✓ Member fetched: ZK User ID = 1001
2. ✓ For each device in access rule:
   - Connect to device (ZK or BioTime)
   - Add/update user (1001, "Ahmed Al-Rashid")
   - Set access permissions
   - Set time restrictions (if any)
3. ✓ Sync status updated
4. ✓ Last sync timestamp recorded

#### 6.4 Monitor Access Logs

```python
# Get today's access logs
logs = frappe.get_all("Access Log", filters={
    "event_time": [">=", "2026-02-15 00:00:00"],
    "event_time": ["<", "2026-02-16 00:00:00"]
}, fields=["*"], order_by="event_time desc")

for log in logs:
    print(f"{log.event_time} | {log.member} | {log.event_type} | {log.device}")
```

**Sample Output**:
```
2026-02-15 09:05:23 | MEM-001 | Entry | ZK-DT-001
2026-02-15 12:34:12 | MEM-002 | Entry | ZK-DT-001
2026-02-15 17:23:45 | MEM-001 | Exit  | ZK-DT-001
2026-02-15 18:45:11 | MEM-002 | Exit  | ZK-DT-001
```

### Phase 7: Financial Management

#### 7.1 Location Expenses - Create with Invoice

```python
expense = frappe.new_doc("Location Expense")
expense.location = "DT-001"
expense.expense_date = "2026-02-01"
expense.expense_type = "Rent"
expense.amount = 50000
expense.vendor = "Property Owner LLC"  # Must exist as Supplier
expense.description = "Monthly rent for February 2026"
expense.payment_status = "Pending"
expense.invoice_number = "INV-2026-02-001"
expense.is_recurring = 1
expense.period_month = "February"
expense.period_year = 2026
expense.insert()

# Create Purchase Invoice
expense.create_purchase_invoice()
```

**What Happens**:
1. ✓ Expense Item created: "EXP-RENT"
2. ✓ Purchase Invoice created
   - Supplier: Property Owner LLC
   - Amount: 50,000 SAR
   - Expense Account: Rent - [Company]
   - Cost Center: DT-001 - [Company]
3. ✓ expense.purchase_invoice linked

#### 7.2 Create Payment Entry for Paid Expense

```python
# Update payment status
expense = frappe.get_doc("Location Expense", expense.name)
expense.payment_status = "Paid"
expense.payment_date = "2026-02-05"
expense.save()

# Create payment entry
expense.create_payment_entry()
```

**What Happens**:
1. ✓ Payment Entry created
   - Payment Type: Pay
   - Party: Property Owner LLC
   - Amount: 50,000 SAR
   - From: Cash/Bank Account
   - To: Payable Account
2. ✓ Payment Entry submitted
3. ✓ Purchase Invoice marked as paid

#### 7.3 Auto Create Both (One-Click)

```python
expense = frappe.new_doc("Location Expense")
expense.location = "DT-001"
expense.expense_date = "2026-02-01"
expense.expense_type = "Electricity"
expense.amount = 8000
expense.vendor = "Power Company"
expense.description = "Electricity bill for February"
expense.payment_status = "Paid"
expense.payment_date = "2026-02-05"
expense.invoice_number = "ELEC-2026-02"
expense.insert()

# One-click automation
result = expense.auto_create_invoice_and_payment()
```

**Result**:
```json
{
  "purchase_invoice": "ACC-PINV-2026-00002",
  "grand_total": 8000.0,
  "payment_entry": "ACC-PAY-2026-00001",
  "paid_amount": 8000.0
}
```

---

## Test Cases A-Z

### Test Case 1: Complete Member Onboarding

**Objective**: Test full member creation with auto-generation

**Prerequisites**: None

**Steps**:
1. Create new member via UI or API
2. Verify Customer auto-creation
3. Verify ZK User ID generation
4. Verify document naming

**Test Data**:
```python
member_data = {
    "member_name": "Sara Al-Mansour",
    "member_code": "MEM-TEST-001",
    "member_type": "Individual",
    "primary_email": "sara.mansour@test.com",
    "primary_mobile": "+966-55-1112233",
    "join_date": "2026-02-01",
    "status": "Active"
}
```

**Expected Results**:
- ✓ Member created with name = MEM-TEST-001
- ✓ Title displays "Sara Al-Mansour"
- ✓ ERPNext Customer created: "Sara Al-Mansour"
- ✓ ZK User ID assigned (e.g., 1003)
- ✓ member_code is unique
- ✓ Searchable by name, email, mobile

**Validation**:
```python
member = frappe.get_doc("Member", "MEM-TEST-001")
assert member.member_name == "Sara Al-Mansour"
assert member.zk_user_id is not None
assert frappe.db.exists("Customer", member.customer)
```

---

### Test Case 2: Space Availability Check

**Objective**: Verify availability checking prevents double booking

**Prerequisites**:
- Space DT-A101 exists
- Contract CTR-2026-00001 occupies DT-A101

**Steps**:
1. Check availability of occupied space
2. Verify rejection
3. Check availability of free space
4. Verify acceptance

**Test Data**:
```python
# Test 1: Occupied space
from grm_management.grm_management.api import check_space_availability

result1 = check_space_availability(
    space="DT-A101",
    date="2026-02-15",
    start_time="09:00:00",
    end_time="17:00:00"
)

# Test 2: Free space
result2 = check_space_availability(
    space="DT-HD05",
    date="2026-02-15",
    start_time="09:00:00",
    end_time="17:00:00"
)
```

**Expected Results**:
```python
# result1
{
    "available": False,
    "message": "Space is occupied by contract or has conflicting bookings"
}

# result2
{
    "available": True,
    "space": "DT-HD05",
    "date": "2026-02-15"
}
```

---

### Test Case 3: Contract Lifecycle

**Objective**: Test complete contract workflow from draft to termination

**Prerequisites**:
- Member MEM-001 exists
- Space DT-A101 is Available

**Steps**:

**3.1 Create Draft Contract**
```python
contract = frappe.new_doc("GRM Contract")
contract.member = "MEM-001"
contract.contract_type = "Space Rental"
contract.status = "Draft"
contract.start_date = "2026-03-01"
contract.end_date = "2026-09-01"
contract.monthly_rent = 12000
contract.security_deposit = 12000
contract.append("spaces", {"space": "DT-A101", "monthly_rent": 12000})
contract.insert()
contract_name = contract.name
```

**Expected**: Contract in Draft, space still Available

**3.2 Approve Contract**
```python
contract = frappe.get_doc("GRM Contract", contract_name)
contract.approve()
```

**Expected**:
- Contract status = Active
- Space status = Occupied
- Access Rule created
- Invoice created (24,000 SAR)

**3.3 Check Statistics**
```python
space = frappe.get_doc("Space", "DT-A101")
assert space.status == "Occupied"
assert space.current_member == "MEM-001"

member = frappe.get_doc("Member", "MEM-001")
assert member.active_contracts == 1
```

**3.4 Terminate Contract**
```python
contract = frappe.get_doc("GRM Contract", contract_name)
contract.terminate(reason="Member relocating")
```

**Expected**:
- Contract status = Terminated
- Space status = Available
- Access Rules deactivated
- Space.current_member = None

---

### Test Case 4: Membership Usage Tracking

**Objective**: Test access counter management

**Prerequisites**:
- Member MEM-002 exists
- Package "Flexi Desk - 10 Days" exists

**Steps**:

**4.1 Create and Activate Membership**
```python
membership = frappe.new_doc("Membership")
membership.member = "MEM-002"
membership.package = "Flexi Desk - 10 Days"
membership.start_date = "2026-03-01"
membership.end_date = "2026-03-31"
membership.package_price = 2500
membership.insert()

membership = frappe.get_doc("Membership", membership.name)
membership.activate()
```

**Expected**:
- total_access_allowed = 10
- access_used = 0
- entries_remaining = 10

**4.2 Use Access (via booking check-in)**
```python
# Create booking with membership
booking = frappe.new_doc("Booking")
booking.member = "MEM-002"
booking.space = "DT-HD05"
booking.booking_date = "2026-03-05"
booking.start_time = "09:00:00"
booking.end_time = "17:00:00"
booking.rate_type = "Package"
booking.membership = membership.name
booking.insert()
booking.confirm()
booking.check_in()
```

**Expected**:
- access_used = 1
- entries_remaining = 9

**4.3 Exhaust Access Limit**
```python
# Use all 10 entries
for i in range(9):  # Already used 1
    membership.decrement_access(1)

# Try to use when exhausted
try:
    membership.decrement_access(1)
    assert False, "Should have thrown error"
except Exception as e:
    assert "No access remaining" in str(e)
```

**4.4 Pause and Resume**
```python
# Pause on 2026-03-15
membership = frappe.get_doc("Membership", membership.name)
membership.pause(reason="Member on vacation")

# Wait 10 days, resume on 2026-03-25
membership.pause_end = "2026-03-25"
membership.resume()
```

**Expected**:
- Pause duration: 10 days
- end_date extended to 2026-04-10 (31 + 10)

---

### Test Case 5: Booking with Overtime

**Objective**: Test overtime calculation and charges

**Prerequisites**:
- Space DT-HD05 available
- Member MEM-001 exists

**Steps**:

**5.1 Create and Confirm Booking**
```python
booking = frappe.new_doc("Booking")
booking.member = "MEM-001"
booking.space = "DT-HD05"
booking.booking_date = "2026-03-10"
booking.start_time = "09:00:00"
booking.end_time = "17:00:00"  # 8 hours
booking.rate_type = "Daily Rate"
booking.daily_rate = 300
booking.insert()
booking.confirm()
```

**5.2 Check-in on Time**
```python
# Simulate check-in at 09:05
booking.check_in()
```

**Expected**:
- actual_check_in recorded
- Status = Checked-In

**5.3 Check-out Late (Overtime)**
```python
# Simulate check-out at 19:30 (2.5 hours late)
import frappe.utils
booking.actual_check_out = frappe.utils.add_to_date(
    frappe.utils.get_datetime(f"{booking.booking_date} {booking.end_time}"),
    hours=2.5
)
booking.check_out()
```

**Expected Calculation**:
- Planned end: 17:00:00
- Actual end: 19:30:00
- Overtime: 2.5 hours
- Hourly rate: 300/8 = 37.5 SAR/hour
- Overtime charge: 2.5 × 37.5 × 1.5 = 140.625 SAR
- overtime_charges = 140.625

---

### Test Case 6: Access Device Sync

**Objective**: Test device synchronization for Direct ZK mode

**Prerequisites**:
- ZK device at 192.168.1.100:4370 (or mock)
- Member MEM-001 with active access

**Steps**:

**6.1 Create Device**
```python
device = frappe.new_doc("Access Device")
device.device_name = "Test ZK Device"
device.device_code = "ZK-TEST-001"
device.device_type = "Fingerprint"
device.location = "DT-001"
device.connection_mode = "Direct ZK"
device.ip_address = "192.168.1.100"
device.port = 4370
device.insert()
```

**6.2 Test Connection**
```python
result = device.test_connection()
```

**Expected** (with real device):
```json
{
  "status": "success",
  "message": "Connected to device successfully"
}
```

**6.3 Sync User to Device**
```python
# Get access rule
access_rule = frappe.get_last_doc("Access Rule", {
    "member": "MEM-001",
    "status": "Active"
})

# Add device to rule
access_rule.append("devices", {"access_device": "ZK-TEST-001"})
access_rule.save()

# Sync
access_rule.sync_to_devices()
```

**Expected**:
- User 1001 added to device
- Name: "Ahmed Al-Rashid"
- Sync status: "Synced"

**6.4 Sync Attendance**
```python
device.sync_attendance()
```

**Expected**:
- Attendance records fetched from device
- Access Logs created for each entry/exit

---

### Test Case 7: BioTime API Integration

**Objective**: Test BioTime API connectivity and sync

**Prerequisites**:
- BioTime server at 192.168.1.10:8000
- Valid credentials

**Steps**:

**7.1 Configure BioTime**
```python
biotime = frappe.get_doc("BioTime Settings", "BioTime Settings")
biotime.enabled = 1
biotime.server_url = "192.168.1.10"
biotime.port = 8000
biotime.username = "admin"
biotime.set_value("password", "admin123")
biotime.save()
```

**7.2 Get Token**
```python
biotime.get_token()
```

**Expected**:
- access_token set
- token_expiry set (24 hours from now)

**7.3 Sync Devices from BioTime**
```python
biotime.sync_devices()
```

**Expected**:
- Access Devices created/updated from BioTime
- connection_mode = "BioTime API"

**7.4 Sync Attendance**
```python
biotime.sync_attendance()
```

**Expected**:
- Transaction records fetched
- Access Logs created

---

### Test Case 8: Location Expense to Purchase Invoice

**Objective**: Test expense to PI workflow

**Prerequisites**:
- Supplier "Test Vendor" exists
- Location DT-001 exists

**Steps**:

**8.1 Create Expense**
```python
expense = frappe.new_doc("Location Expense")
expense.location = "DT-001"
expense.expense_date = "2026-03-01"
expense.expense_type = "Maintenance"
expense.amount = 3500
expense.vendor = "Test Vendor"
expense.description = "HVAC maintenance"
expense.payment_status = "Pending"
expense.invoice_number = "MNT-2026-03"
expense.insert()
```

**8.2 Create Purchase Invoice**
```python
result = expense.create_purchase_invoice()
```

**Expected**:
```json
{
  "purchase_invoice": "ACC-PINV-2026-XXXXX",
  "grand_total": 3500.0
}
```

**Verify**:
```python
pi = frappe.get_doc("Purchase Invoice", result["purchase_invoice"])
assert pi.supplier == "Test Vendor"
assert pi.grand_total == 3500
assert pi.items[0].item_code == "EXP-MAINTENANCE"
```

**8.3 Create Payment Entry**
```python
expense.payment_status = "Paid"
expense.payment_date = "2026-03-05"
expense.save()

result = expense.create_payment_entry()
```

**Expected**:
```json
{
  "payment_entry": "ACC-PAY-2026-XXXXX",
  "paid_amount": 3500.0
}
```

**Verify**:
```python
pe = frappe.get_doc("Payment Entry", result["payment_entry"])
assert pe.payment_type == "Pay"
assert pe.party == "Test Vendor"
assert pe.paid_amount == 3500
assert pe.docstatus == 1  # Submitted
```

---

### Test Case 9: Automated Tasks

**Objective**: Test scheduled tasks execution

**9.1 Hourly Task - Sync Attendance**
```python
from grm_management.grm_management.scheduled_tasks import hourly

# Run hourly task
hourly()
```

**Expected**:
- All devices with auto_sync=1 synced
- BioTime attendance fetched
- Device health checked
- Active bookings access checked

**9.2 Daily Task - Expire Contracts**
```python
from grm_management.grm_management.scheduled_tasks import daily

# Create expired contract (end_date in past)
contract = frappe.get_doc("GRM Contract", "CTR-2026-00001")
contract.end_date = frappe.utils.add_days(frappe.utils.today(), -1)
contract.save()

# Run daily task
daily()
```

**Expected**:
- Contract status = Expired
- Spaces freed
- Access deactivated

**9.3 Monthly Task - Generate Invoices**
```python
from grm_management.grm_management.scheduled_tasks import monthly

monthly()
```

**Expected**:
- Monthly invoices created for all active contracts
- Membership renewals processed
- Monthly reports generated

---

### Test Case 10: API Endpoints

**Objective**: Test all REST API endpoints

**10.1 Check Availability API**
```bash
curl -X GET "http://localhost:8000/api/method/grm_management.grm_management.api.check_space_availability" \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "space=DT-HD05" \
  -d "date=2026-03-15" \
  -d "start_time=09:00:00" \
  -d "end_time=17:00:00"
```

**Expected Response**:
```json
{
  "message": {
    "available": true,
    "space": "DT-HD05",
    "date": "2026-03-15"
  }
}
```

**10.2 Get Member Access Status**
```bash
curl -X GET "http://localhost:8000/api/method/grm_management.grm_management.api.get_member_access_status" \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "member=MEM-001"
```

**Expected Response**:
```json
{
  "message": {
    "member": "MEM-001",
    "has_access": true,
    "active_contracts": 1,
    "active_memberships": 0,
    "access_rules": [
      {
        "name": "ACC-RULE-00001",
        "rule_type": "Contract",
        "status": "Active",
        "valid_from": "2026-03-01",
        "valid_to": "2026-09-01"
      }
    ]
  }
}
```

**10.3 Quick Check-in**
```bash
curl -X POST "http://localhost:8000/api/method/grm_management.grm_management.api.quick_check_in" \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "member=MEM-001" \
  -d "location=DT-001"
```

**Expected Response**:
```json
{
  "message": {
    "status": "success",
    "member": "MEM-001",
    "location": "DT-001",
    "timestamp": "2026-03-15 09:15:23",
    "access_log": "ACC-LOG-00045"
  }
}
```

**10.4 Get Location Dashboard**
```bash
curl -X GET "http://localhost:8000/api/method/grm_management.grm_management.api.get_location_dashboard" \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "location=DT-001"
```

**Expected Response**:
```json
{
  "message": {
    "location": "DT-001",
    "total_spaces": 25,
    "available_spaces": 12,
    "occupied_spaces": 10,
    "reserved_spaces": 3,
    "occupancy_rate": 40.0,
    "todays_bookings": 5,
    "active_contracts": 8,
    "todays_checkins": 15
  }
}
```

---

## Complete Test Cycle (A to Z)

### Full Scenario: New Member → Contract → Access → Invoice → Payment

```python
# ============================================================
# COMPLETE TEST CYCLE - COWORKING SPACE BOOKING & MANAGEMENT
# ============================================================

import frappe
from frappe.utils import nowdate, add_days, add_months

# Step 1: CREATE LOCATION (If not exists)
# ============================================================
if not frappe.db.exists("GRM Location", "DT-001"):
    location = frappe.new_doc("GRM Location")
    location.location_name = "Downtown Coworking Hub"
    location.location_code = "DT-001"
    location.status = "Active"
    location.city = "Riyadh"
    location.country = "Saudi Arabia"
    location.rent_cost = 50000
    location.utilities_cost = 8000
    location.maintenance_cost = 5000
    location.staff_cost = 25000
    location.insert()
    print("✓ Location created: DT-001")

# Step 2: CREATE SPACE TYPE
# ============================================================
if not frappe.db.exists("Space Type", "PO"):
    space_type = frappe.new_doc("Space Type")
    space_type.type_name = "Private Office"
    space_type.type_code = "PO"
    space_type.default_capacity = 4
    space_type.allow_daily = 1
    space_type.allow_monthly = 1
    space_type.allow_long_term = 1
    space_type.daily_rate = 500
    space_type.monthly_rate = 10000
    space_type.insert()
    print("✓ Space Type created: PO")

# Step 3: CREATE SPACE
# ============================================================
if not frappe.db.exists("Space", "DT-PO-101"):
    space = frappe.new_doc("Space")
    space.space_name = "Executive Office 101"
    space.space_code = "DT-PO-101"
    space.location = "DT-001"
    space.space_type = "PO"
    space.capacity = 4
    space.area_sqm = 30
    space.status = "Available"
    space.insert()
    print("✓ Space created: DT-PO-101")

# Step 4: CREATE MEMBER
# ============================================================
member = frappe.new_doc("Member")
member.member_name = "Khalid Al-Otaibi"
member.member_code = "MEM-TEST-A01"
member.member_type = "Individual"
member.primary_email = "khalid.otaibi@test.com"
member.primary_mobile = "+966-50-9988776"
member.join_date = nowdate()
member.status = "Active"
member.insert()
print(f"✓ Member created: {member.name}")
print(f"  - Customer: {member.customer}")
print(f"  - ZK User ID: {member.zk_user_id}")

# Step 5: CHECK SPACE AVAILABILITY
# ============================================================
from grm_management.grm_management.api import check_space_availability

availability = check_space_availability(
    space="DT-PO-101",
    date=add_days(nowdate(), 7),
    start_time="08:00:00",
    end_time="18:00:00"
)
print(f"✓ Space availability checked: {availability['available']}")

# Step 6: CREATE CONTRACT
# ============================================================
contract = frappe.new_doc("GRM Contract")
contract.member = member.name
contract.contract_type = "Space Rental"
contract.status = "Draft"
contract.start_date = add_days(nowdate(), 7)
contract.end_date = add_months(add_days(nowdate(), 7), 6)
contract.monthly_rent = 10000
contract.security_deposit = 10000
contract.notice_period_days = 30
contract.append("spaces", {
    "space": "DT-PO-101",
    "monthly_rent": 10000
})
contract.append("granted_users", {
    "user_name": member.member_name,
    "email": member.primary_email,
    "access_granted": 1
})
contract.insert()
print(f"✓ Contract created: {contract.name} (Draft)")

# Step 7: APPROVE CONTRACT
# ============================================================
contract.approve()
print(f"✓ Contract approved: {contract.name}")
print(f"  - Status: {contract.status}")

# Verify space occupation
space = frappe.get_doc("Space", "DT-PO-101")
print(f"  - Space status: {space.status}")
print(f"  - Current member: {space.current_member}")

# Step 8: VERIFY ACCESS RULE CREATED
# ============================================================
access_rules = frappe.get_all("Access Rule", filters={
    "member": member.name,
    "status": "Active"
}, fields=["name", "rule_type", "reference_name"])
print(f"✓ Access rules created: {len(access_rules)}")
for rule in access_rules:
    print(f"  - {rule.name}: {rule.rule_type} → {rule.reference_name}")

# Step 9: CHECK INVOICE CREATED
# ============================================================
invoices = frappe.get_all("Sales Invoice", filters={
    "customer": member.customer
}, fields=["name", "grand_total", "outstanding_amount"])
print(f"✓ Invoices created: {len(invoices)}")
for inv in invoices:
    print(f"  - {inv.name}: {inv.grand_total} SAR (Outstanding: {inv.outstanding_amount})")

# Step 10: CREATE LOCATION EXPENSE
# ============================================================
# First, ensure supplier exists
if not frappe.db.exists("Supplier", "Test Property Owner"):
    supplier = frappe.new_doc("Supplier")
    supplier.supplier_name = "Test Property Owner"
    supplier.supplier_group = "Services"
    supplier.insert()
    print("✓ Supplier created: Test Property Owner")

expense = frappe.new_doc("Location Expense")
expense.location = "DT-001"
expense.expense_date = nowdate()
expense.expense_type = "Rent"
expense.amount = 50000
expense.vendor = "Test Property Owner"
expense.description = "Monthly rent"
expense.payment_status = "Paid"
expense.payment_date = nowdate()
expense.invoice_number = "RENT-2026-02"
expense.insert()
print(f"✓ Location expense created: {expense.name}")

# Step 11: AUTO CREATE PURCHASE INVOICE & PAYMENT
# ============================================================
result = expense.auto_create_invoice_and_payment()
print("✓ Financial documents created:")
print(f"  - Purchase Invoice: {result.get('purchase_invoice')}")
print(f"  - Payment Entry: {result.get('payment_entry')}")

# Step 12: SETUP ACCESS DEVICE
# ============================================================
device = frappe.new_doc("Access Device")
device.device_name = "Main Entrance - Test"
device.device_code = "ZK-TEST-MAIN"
device.device_type = "Fingerprint"
device.location = "DT-001"
device.connection_mode = "Direct ZK"
device.ip_address = "192.168.1.100"
device.port = 4370
device.status = "Offline"
device.auto_sync = 0  # Manual sync for testing
device.insert()
print(f"✓ Access device created: {device.name}")

# Step 13: ADD DEVICE TO ACCESS RULE & SYNC
# ============================================================
access_rule = frappe.get_doc("Access Rule", access_rules[0].name)
access_rule.append("devices", {"access_device": device.name})
access_rule.save()
print("✓ Device added to access rule")

# Try to sync (will fail without real device, but code path tested)
try:
    access_rule.sync_to_devices()
    print("✓ Access synced to devices")
except Exception as e:
    print(f"⚠ Sync failed (expected without real device): {str(e)[:100]}")

# Step 14: UPDATE LOCATION STATISTICS
# ============================================================
location = frappe.get_doc("GRM Location", "DT-001")
location.update_statistics()
print("✓ Location statistics updated:")
print(f"  - Total spaces: {location.total_spaces}")
print(f"  - Occupied: {location.occupied_spaces}")
print(f"  - Available: {location.available_spaces}")
print(f"  - Occupancy rate: {location.occupancy_rate}%")

# Step 15: GET LOCATION DASHBOARD
# ============================================================
from grm_management.grm_management.api import get_location_dashboard

dashboard = get_location_dashboard("DT-001")
print("✓ Location dashboard:")
print(f"  - Total spaces: {dashboard['total_spaces']}")
print(f"  - Occupancy rate: {dashboard['occupancy_rate']}%")
print(f"  - Active contracts: {dashboard['active_contracts']}")

# ============================================================
# TEST CYCLE COMPLETE
# ============================================================
print("\n" + "="*60)
print("COMPLETE TEST CYCLE FINISHED SUCCESSFULLY!")
print("="*60)
print("\nCreated Documents:")
print(f"  - Member: {member.name}")
print(f"  - Contract: {contract.name}")
print(f"  - Space: DT-PO-101 (Status: {space.status})")
print(f"  - Access Rule: {access_rules[0].name}")
print(f"  - Invoice: {invoices[0].name if invoices else 'N/A'}")
print(f"  - Expense: {expense.name}")
print(f"  - Purchase Invoice: {result.get('purchase_invoice')}")
print(f"  - Payment: {result.get('payment_entry')}")
print("="*60)
```

---

## Summary

This comprehensive test guide covers:

✅ **Complete module documentation** with data flow and architecture
✅ **Step-by-step workflows** for all major features
✅ **10 detailed test cases** covering individual features
✅ **Full A-Z test cycle** combining all features
✅ **API testing examples** with curl commands
✅ **Automated tasks testing**
✅ **Expected results** for every test
✅ **Validation queries** to verify outcomes

**Run the complete test**:
```bash
bench --site site1.local execute "import frappe; exec(open('/home/frappe/frappe-bench/apps/grm_management/TEST_GUIDE.md').read().split('```python')[1].split('```')[0])"
```

Or run individual test cases as needed!
