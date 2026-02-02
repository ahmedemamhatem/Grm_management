# GRM Management Module - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [Module Architecture](#module-architecture)
3. [Master Data Setup](#master-data-setup)
4. [Transactions & Operations](#transactions--operations)
5. [Complete Testing Workflow](#complete-testing-workflow)
6. [API Reference](#api-reference)

---

## Overview

The GRM (Guest Relationship Management) module is a comprehensive coworking space management system built on Frappe/ERPNext. It handles:

- **Location Management**: Multiple coworking locations/branches
- **Space Management**: Private offices, hot desks, meeting rooms, dedicated desks
- **Member Management**: Individual and company members with customer integration
- **Contract Management**: Space rental agreements with approval workflow
- **Membership Management**: Package-based memberships (flexi desk, meeting room hours)
- **Booking Management**: Hourly/daily space bookings
- **Access Control**: ZKTeco device integration for biometric access
- **Financial Integration**: ERPNext Sales Invoice and Payment Entry

---

## Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MASTER DATA (Setup First)                    │
├─────────────────────────────────────────────────────────────────┤
│  GRM Location  →  Space Type  →  Space  →  Amenity             │
│       ↓              ↓            ↓                             │
│  Operating     Default       Pricing &                          │
│  Hours         Pricing       Availability                       │
├─────────────────────────────────────────────────────────────────┤
│  Member  →  Creates Customer in ERPNext automatically           │
│  Package →  Extended from ERPNext Package (custom fields)       │
│  Access Device → ZKTeco fingerprint/face recognition devices    │
├─────────────────────────────────────────────────────────────────┤
│                     TRANSACTIONS                                 │
├─────────────────────────────────────────────────────────────────┤
│  GRM Contract  →  Space rental agreements (monthly/yearly)      │
│  Membership    →  Package subscriptions (flexi desk, etc.)      │
│  Booking       →  Hourly/daily space reservations               │
├─────────────────────────────────────────────────────────────────┤
│                     INTEGRATION                                  │
├─────────────────────────────────────────────────────────────────┤
│  Sales Invoice    →  Billing for contracts, memberships         │
│  Payment Entry    →  Payment recording                          │
│  Access Rule      →  Biometric access permissions               │
│  Access Log       →  Entry/exit tracking                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Master Data Setup

### Step 1: Create GRM Locations

**Path**: `Coworking Space > GRM Location > + Add GRM Location`

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Location Name | Full name | "Downtown Business Hub" |
| Location Code | Unique code (auto-naming) | "DTH-001" |
| Status | Active/Inactive/Under Renovation | "Active" |
| Email | Contact email | "downtown@company.com" |
| Phone | Contact number | "+966-11-1234567" |

**Address Fields**:
- Address Line 1, Address Line 2
- City, State, Postal Code, Country

**Operating Hours** (Text field):
```
Mon-Fri: 8:00 AM - 8:00 PM
Sat-Sun: 10:00 AM - 6:00 PM
```

**Example**:
```
Location Name: Downtown Business Hub
Location Code: DTH-001
Status: Active
Email: downtown@cowork.sa
Phone: +966-11-2345678
Address: King Fahd Road, Tower A, Floor 15
City: Riyadh
Country: Saudi Arabia
```

---

### Step 2: Create Space Types

**Path**: `Coworking Space > Space Type > + Add Space Type`

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Type Name | Display name | "Private Office" |
| Type Code | Unique code (auto-naming) | "PO" |
| Default Capacity | Standard capacity | 4 |
| Description | Type description | "Fully furnished private office" |

**Booking Options**:
| Field | PO | HD | DD | MR |
|-------|-----|-----|-----|-----|
| Allow Hourly | No | Yes | No | Yes |
| Allow Daily | Yes | Yes | No | Yes |
| Allow Monthly | Yes | Yes | Yes | No |
| Allow Long Term | Yes | No | Yes | No |

**Pricing**:
| Field | Example |
|-------|---------|
| Hourly Rate | 150 SAR |
| Daily Rate | 600 SAR |
| Monthly Rate | 12,000 SAR |

**Create these Space Types**:

1. **Private Office (PO)**
   - Capacity: 4
   - Monthly: Yes, Daily: Yes
   - Monthly Rate: 12,000 SAR

2. **Hot Desk (HD)**
   - Capacity: 1
   - Hourly: Yes, Daily: Yes
   - Hourly Rate: 50 SAR, Daily Rate: 300 SAR

3. **Dedicated Desk (DD)**
   - Capacity: 1
   - Monthly: Yes
   - Monthly Rate: 3,500 SAR

4. **Meeting Room (MR)**
   - Capacity: 8
   - Hourly: Yes, Daily: Yes
   - Hourly Rate: 150 SAR, Daily Rate: 1,000 SAR

---

### Step 3: Create Amenities

**Path**: `Coworking Space > Amenity > + Add Amenity`

**Required Fields**:
| Field | Description |
|-------|-------------|
| Amenity Name | "High-Speed WiFi" |
| Amenity Code | "WIFI" |
| Category | Technology/Furniture/Service/Facility |
| Is Chargeable | Yes/No |
| Price | If chargeable |

**Create these Amenities**:
```
1. High-Speed WiFi (WIFI) - Technology - Free
2. Printer/Scanner (PRINT) - Technology - Chargeable (0.50 SAR/page)
3. Whiteboard (WB) - Furniture - Free
4. TV/Monitor (TV) - Technology - Free
5. Coffee/Tea (COFFEE) - Service - Free
6. Air Conditioning (AC) - Facility - Free
7. Phone Booth (PHONE) - Facility - Free
8. Locker (LOCKER) - Facility - Chargeable (200 SAR/month)
```

---

### Step 4: Create Spaces

**Path**: `Coworking Space > Space > + Add Space`

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Space Name | Display name | "Private Office A-101" |
| Space Code | Unique code (auto-naming) | "DTH-PO-A101" |
| Location | Link to GRM Location | "DTH-001" |
| Space Type | Link to Space Type | "PO" |
| Status | Available/Occupied/Reserved/Maintenance | "Available" |
| Capacity | Number of people | 4 |
| Area (sqm) | Floor area | 25 |
| Floor | Floor location | "15th Floor" |

**Pricing** (if custom):
- Use Custom Pricing: Yes/No
- Custom Hourly/Daily/Monthly Rate

**Create Spaces for Each Location**:

**DTH-001 (Downtown):**
```
Private Offices (3):
- DTH-PO-A101, DTH-PO-A102, DTH-PO-A103

Hot Desks (5):
- DTH-HD-001 to DTH-HD-005

Dedicated Desks (3):
- DTH-DD-001 to DTH-DD-003

Meeting Rooms (2):
- DTH-MR-001, DTH-MR-002
```

---

### Step 5: Create Members

**Path**: `Coworking Space > Member > + Add Member`

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Member Name | Full name/Company name | "Ahmed Al-Rashid" |
| Member Code | Unique code (auto-naming) | "MEM-001" |
| Member Type | Individual/Company | "Individual" |
| Primary Email | Contact email | "ahmed@email.com" |
| Primary Mobile | Mobile number | "+966-50-1234567" |
| Status | Active/Inactive/Suspended/Blacklisted | "Active" |

**Identification**:
| Field | Individual | Company |
|-------|------------|---------|
| ID Type | National ID/Passport | CR |
| ID/CR Number | 1023456789 | 7012345678 |
| Tax ID | - | 300123456700003 |

**Auto-Created**:
- **Customer**: Creates ERPNext Customer automatically with same name
- **ZK User ID**: Auto-assigned for biometric access (1001, 1002, etc.)

**Create Sample Members**:
```
1. Individual: Ahmed Al-Rashid (MEM-001)
   - Email: ahmed@email.com
   - Mobile: +966-50-1234567
   - ID: National ID - 1023456789

2. Company: TechStart Solutions LLC (MEM-002)
   - Email: info@techstart.sa
   - Mobile: +966-50-9876543
   - CR: 7012345678
   - Tax ID: 300123456700003

3. Individual: Sara Al-Mansour (MEM-003)
   - Email: sara@email.com
   - Mobile: +966-55-1112233
```

---

### Step 6: Create Packages (Optional - for Memberships)

**Path**: `Setup > Package > + Add Package`

**Note**: Package is a core Frappe DocType extended with GRM custom fields.

**Required Fields**:
| Field | Description |
|-------|-------------|
| Package Name | Must be alphanumeric only (e.g., "flexidesk10") |
| Package Code | Unique code (e.g., "FD10") |
| Description | Package description |
| Package Category | Hot Desk/Dedicated/Private Office/Meeting Room/Virtual |
| Status | Active/Inactive |

**Create Packages**:
```
1. flexidesk10 (FD10)
   - Category: Hot Desk
   - Description: 10 days hot desk access per month

2. flexidesk20 (FD20)
   - Category: Hot Desk
   - Description: 20 days hot desk access per month

3. meetingroom10 (MR10)
   - Category: Meeting Room
   - Description: 10 hours meeting room per month
```

---

### Step 7: Create Access Devices (Optional - for Access Control)

**Path**: `Coworking Space > Access Device > + Add Access Device`

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Device Name | Display name | "Main Entrance - Fingerprint" |
| Device Code | Unique code | "ZK-DTH-001" |
| Device Type | Fingerprint/Face Recognition/Card Reader | "Fingerprint" |
| Location | Link to GRM Location | "DTH-001" |
| IP Address | Device IP | "192.168.1.100" |
| Port | Device port | 4370 |
| Status | Online/Offline/Maintenance | "Online" |

**Connection Modes**:
- **Direct ZK**: Direct connection to ZKTeco device
- **BioTime API**: Via BioTime server

---

## Transactions & Operations

### Transaction 1: GRM Contract (Space Rental)

**Use Case**: Long-term space rental (monthly/yearly)

**Path**: `Coworking Space > GRM Contract > + Add GRM Contract`

**Workflow**:
```
Draft → Active → (Renewal/Termination) → Completed/Terminated
```

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Contract Number | Manual entry (required) | "CTR-2026-001" |
| Member | Link to Member | "MEM-001" |
| Contract Type | Space Rental/Membership/Combination | "Space Rental" |
| Status | Draft/Active/Expired/Terminated | "Draft" |
| Start Date | Contract start | "2026-02-01" |
| End Date | Contract end | "2026-07-31" |
| Monthly Rent | Total monthly amount | 12,000 SAR |
| Security Deposit | Refundable deposit | 12,000 SAR |

**Child Tables**:
- **Spaces**: Add contracted spaces
- **Granted Users**: Add authorized users for access

**Process**:
1. Create contract in Draft status
2. Add spaces to contract
3. Set billing terms
4. Submit/Approve contract → Status changes to Active
5. System can auto-create Sales Invoice for billing

---

### Transaction 2: Membership (Package Subscription)

**Use Case**: Flexi desk passes, meeting room hours, etc.

**Path**: `Coworking Space > Membership > + Add Membership`

**Workflow**:
```
Draft → Active → Expired/Cancelled
```

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Membership Number | Auto-generated | "MEM-2026-00001" |
| Member | Link to Member | "MEM-003" |
| Package | Link to Package | "flexidesk10" |
| Status | Draft/Active/Expired/Cancelled | "Draft" |
| Start Date | Membership start | "2026-02-01" |
| End Date | Membership end | "2026-02-28" |

**Usage Tracking**:
| Field | Description |
|-------|-------------|
| Desk Days Allowed | From package |
| Desk Days Used | Consumed days |
| Meeting Hours Allowed | From package |
| Meeting Hours Used | Consumed hours |

---

### Transaction 3: Booking (Space Reservation)

**Use Case**: Hourly/daily space reservations (hot desks, meeting rooms)

**Path**: `Coworking Space > Booking > + Add Booking`

**Workflow**:
```
Draft → Confirmed → Checked-In → Checked-Out → Completed
       ↓
    Cancelled
```

**Required Fields**:
| Field | Description | Example |
|-------|-------------|---------|
| Booking Number | Manual entry (required) | "BKG-2026-001" |
| Member | Link to Member | "MEM-002" |
| Space | Link to Space | "DTH-MR-001" |
| Booking Type | Hourly/Daily | "Hourly" |
| Booking Date | Date of booking | "2026-02-15" |
| Start Time | Start time | "10:00" |
| End Time | End time | "14:00" |
| Status | Draft/Confirmed/Checked-In/etc. | "Draft" |

**Pricing**:
| Field | Description |
|-------|-------------|
| Rate Type | Hourly Rate/Daily Rate |
| Hourly Rate | Rate per hour |
| Daily Rate | Rate per day |
| Subtotal | Calculated amount |
| Discount | Applied discount |
| Total Amount | Final amount |

**Process**:
1. Create booking → Draft
2. Confirm booking → Confirmed
3. Member arrives → Check-In → Checked-In
4. Member leaves → Check-Out → Completed
5. Generate invoice if needed

---

## Complete Testing Workflow

### Test Scenario: New Member Rents Private Office

#### Step 1: Create Master Data
```bash
# Already created via test data generator or manually
```

#### Step 2: Create New Member
```
1. Go to: Coworking Space > Member > + Add Member
2. Enter:
   - Member Name: "Test Company XYZ"
   - Member Code: "MEM-TEST-001"
   - Member Type: Company
   - Primary Email: testxyz@email.com
   - Primary Mobile: +966-50-5555555
   - ID Type: CR
   - CR Number: 1234567890
3. Save
4. Verify: Customer "Test Company XYZ" created in ERPNext
```

#### Step 3: Check Space Availability
```
1. Go to: Coworking Space > Space
2. Filter: Status = "Available", Space Type = "PO"
3. Note available spaces
```

#### Step 4: Create Contract
```
1. Go to: Coworking Space > GRM Contract > + Add
2. Enter:
   - Contract Number: CTR-TEST-001
   - Member: Test Company XYZ (MEM-TEST-001)
   - Contract Type: Space Rental
   - Start Date: (today)
   - End Date: (6 months from today)
   - Monthly Rent: 12,000
   - Security Deposit: 12,000
3. Save (stays in Draft)
```

#### Step 5: Verify Results
```
1. Contract status = Draft
2. Space status = still Available (until approved)
3. No invoice created yet
```

#### Step 6: Approve Contract (if workflow exists)
```
1. Open contract
2. Click "Approve" or change status to Active
3. Verify:
   - Contract status = Active
   - Space status = Occupied (if implemented)
   - Sales Invoice created (if implemented)
```

---

### Test Scenario: Member Books Meeting Room

#### Step 1: Create Booking
```
1. Go to: Coworking Space > Booking > + Add
2. Enter:
   - Booking Number: BKG-TEST-001
   - Member: Ahmed Al-Rashid (MEM-001)
   - Space: DTH-MR-001 (Meeting Room)
   - Booking Type: Hourly
   - Booking Date: (tomorrow)
   - Start Time: 10:00
   - End Time: 14:00
   - Rate Type: Hourly Rate
   - Hourly Rate: 150
3. Save
```

#### Step 2: Confirm Booking
```
1. Status changes to: Draft
2. Click "Confirm" (if button exists) or change status
3. Status = Confirmed
```

#### Step 3: Check-In
```
1. On booking date, open booking
2. Click "Check In" or change status
3. Status = Checked-In
4. Check-in time recorded
```

#### Step 4: Check-Out
```
1. When done, click "Check Out"
2. Status = Completed
3. Check-out time recorded
4. Total hours calculated
```

---

### Test Scenario: Flexi Desk Membership

#### Step 1: Create Membership
```
1. Go to: Coworking Space > Membership > + Add
2. Enter:
   - Member: Sara Al-Mansour (MEM-003)
   - Package: flexidesk10
   - Start Date: 1st of current month
   - End Date: Last day of current month
3. Save
```

#### Step 2: Activate Membership
```
1. Change status to Active
2. Verify:
   - Desk Days Allowed = 10
   - Desk Days Used = 0
```

#### Step 3: Use Membership (Book Hot Desk)
```
1. Create booking for hot desk
2. Link to membership (if field exists)
3. After check-out:
   - Membership Desk Days Used = 1
   - Remaining = 9 days
```

---

## API Reference

### Member API
```python
# Create Member
member = frappe.new_doc("Member")
member.member_name = "John Doe"
member.member_code = "MEM-NEW-001"
member.member_type = "Individual"
member.primary_email = "john@email.com"
member.status = "Active"
member.insert()

# Get Member with Customer
member = frappe.get_doc("Member", "MEM-001")
print(member.customer)  # ERPNext Customer link
print(member.zk_user_id)  # Biometric user ID
```

### Space API
```python
# Check Availability
available_spaces = frappe.get_all("Space",
    filters={
        "location": "DTH-001",
        "space_type": "PO",
        "status": "Available"
    },
    fields=["name", "space_name", "capacity", "monthly_rate"]
)

# Update Space Status
space = frappe.get_doc("Space", "DTH-PO-A101")
space.status = "Occupied"
space.current_member = "MEM-001"
space.save()
```

### Contract API
```python
# Create Contract
contract = frappe.new_doc("GRM Contract")
contract.contract_number = "CTR-API-001"
contract.member = "MEM-001"
contract.contract_type = "Space Rental"
contract.start_date = "2026-02-01"
contract.end_date = "2026-07-31"
contract.monthly_rent = 12000
contract.insert()

# Approve Contract (if method exists)
contract.approve()
```

### Booking API
```python
# Create Booking
booking = frappe.new_doc("Booking")
booking.booking_number = "BKG-API-001"
booking.member = "MEM-001"
booking.space = "DTH-MR-001"
booking.booking_type = "Hourly"
booking.booking_date = "2026-02-15"
booking.start_time = "10:00:00"
booking.end_time = "14:00:00"
booking.hourly_rate = 150
booking.insert()

# Confirm
booking.status = "Confirmed"
booking.save()

# Check In
booking.status = "Checked-In"
booking.check_in_time = frappe.utils.now()
booking.save()
```

### Location Statistics API
```python
# Update Location Statistics
location = frappe.get_doc("GRM Location", "DTH-001")
location.update_statistics()

# Get Location Summary
summary = location.get_location_summary()
print(summary)
# {
#     "location_name": "Downtown Business Hub",
#     "total_spaces": 13,
#     "occupied_spaces": 3,
#     "available_spaces": 10,
#     "occupancy_rate": 23.08,
#     "active_contracts": 2,
#     "today_bookings": 5
# }
```

---

## Quick Reference Cards

### Status Flow - Contract
```
┌────────┐    ┌────────┐    ┌───────────┐
│ Draft  │───>│ Active │───>│ Completed │
└────────┘    └────────┘    └───────────┘
                  │
                  v
            ┌────────────┐
            │ Terminated │
            └────────────┘
```

### Status Flow - Booking
```
┌────────┐    ┌───────────┐    ┌────────────┐    ┌───────────┐
│ Draft  │───>│ Confirmed │───>│ Checked-In │───>│ Completed │
└────────┘    └───────────┘    └────────────┘    └───────────┘
     │              │
     v              v
┌───────────┐  ┌───────────┐
│ Cancelled │  │ No Show   │
└───────────┘  └───────────┘
```

### Status Flow - Membership
```
┌────────┐    ┌────────┐    ┌─────────┐
│ Draft  │───>│ Active │───>│ Expired │
└────────┘    └────────┘    └─────────┘
                  │
                  v
            ┌───────────┐
            │ Cancelled │
            └───────────┘
```

---

## Troubleshooting

### Common Issues

1. **Member not linked to Customer**
   - Check if Customer was auto-created
   - Manually link if needed

2. **Space shows wrong status**
   - Run "Update Statistics" on Location
   - Check if contract is properly approved

3. **Booking overlap**
   - System should validate availability
   - Check booking date/time carefully

4. **Access Device not syncing**
   - Verify IP address and port
   - Check device connection mode
   - Ensure BioTime settings are correct (if using API)

---

## Support

For issues or questions:
- Check Frappe error logs: `bench --site [site] show-error-log`
- Review DocType permissions
- Verify ERPNext integration settings

---

*Document Version: 1.0*
*Last Updated: January 2026*
