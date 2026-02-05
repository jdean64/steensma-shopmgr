# Parts Age Notification Feature - Analysis & Future Enhancement

**Date:** February 5, 2026  
**Purpose:** Customer notification system for parts on order 5+ days

---

## Current Findings (Feb 5, 2026)

### Parts 5+ Days Old Requiring Customer Notification

| Part Number | Age | Status | Customer | Priority |
|---|---|---|---|---|
| **BILP - 812225** | **37 days** | Back-Ordered | **SNYDER'S LAWNCARE** | 🔴 CRITICAL |
| GECP - 0K3717 | 16 days | On Order | Generator Service Vehicles | 🟡 High |
| KAWP - 59011-2059 | 13 days | On Order | DON KOLUDROVICH | 🟡 High |
| TORP - 161-0972 | 8 days | Back-Ordered | Colleen Ritchie | 🟢 Medium |
| TORP - 63-3450 | 7 days | Back-Ordered | BRONCO ASPHALT MAINT | 🟢 Medium |
| TORP - 106-4588-01 | 7 days | Back-Ordered | BRONCO ASPHALT MAINT (related) | 🟢 Medium |
| TORP - 94-8812 | 7 days | Back-Ordered | BRONCO ASPHALT MAINT (related) | 🟢 Medium |

**Total:** 7 parts need customer contact  
**Status:** All 7 are currently visible on dashboard (Back-Ordered or On Order)

---

## Data Source

**File:** `datasheets/Open Back Orders - 2-5-26.txt`  
**Format:** CSV with columns: `Customer, Phone, Part Number, Type, PP, Age, Ordered, Status, Available, Allocated, PO`

**Key Column:** `Age` (index 6) - Number of days since part was ordered

---

## Proposed Feature: Automatic Age-Based Alerts

### Current State
- Dashboard shows parts with status "Back-Ordered" or "On Order"
- **NO age-based filtering or alerts**
- Manual review required to identify parts needing customer notification

### Feature Requirements

#### 1. **Dashboard Enhancement**
- Add "Age" column to Parts Inventory section
- Highlight parts 5+ days old in yellow/orange
- Highlight parts 10+ days old in red
- Sort by age (oldest first) by default

#### 2. **Notification Section** (New Dashboard Card)
Create a new "Customer Notifications" section showing:
- Parts requiring customer contact (5+ days)
- Customer name and phone number (from Open Back Orders file)
- Days waiting
- Quick action: "Mark as Contacted" button

#### 3. **Email Alerts** (Optional - Phase 2)
- Daily email at 8 AM listing parts 5+ days old
- Include customer contact info
- Track contact history

---

## Technical Implementation Notes

### Data Parsing Required
Add age field extraction to `parse_open_back_orders()` function:

```python
# Current return structure:
{
    'part_number': 'BILP - 812225',
    'customer': "SNYDER'S LAWNCARE",
    'status': 'Back-Ordered'
}

# Enhanced structure needed:
{
    'part_number': 'BILP - 812225',
    'customer': "SNYDER'S LAWNCARE",
    'status': 'Back-Ordered',
    'age': 37,  # NEW FIELD
    'phone': '(269) 779-8350',  # NEW FIELD (from column 1)
    'needs_notification': True  # NEW FIELD (age >= 5)
}
```

### Age Thresholds
- **Green (0-4 days):** Normal, no action needed
- **Yellow (5-9 days):** Customer notification recommended
- **Orange (10-14 days):** Follow-up required
- **Red (15+ days):** Urgent - escalate to management

---

## Business Value

### Customer Service Benefits
- **Proactive communication** - Contact customers before they call
- **Improved satisfaction** - Customers appreciate updates on delayed parts
- **Reduced phone calls** - Fewer "where's my part?" inquiries

### Operational Benefits
- **Visibility** - Instant overview of aging parts inventory
- **Accountability** - Track which parts need follow-up
- **Metrics** - Report on average wait times, vendor performance

### Example Use Case
> Every morning at 8 AM, Parts Manager opens dashboard and sees:
> - **3 parts** require customer notification (5-9 days old)
> - **1 part** is critical (15+ days) - calls customer + follows up with vendor
> - Clicks "Mark as Contacted" to log the action

---

## Priority Recommendation

**Phase 1 (Quick Win):**
1. Add "Age" column to existing Parts Inventory display
2. Sort by age descending
3. Add color coding for age thresholds

**Phase 2 (Enhanced):**
4. Create dedicated "Notifications Needed" section
5. Add phone numbers from file
6. "Mark as Contacted" tracking

**Phase 3 (Advanced):**
7. Email alerts for daily notifications
8. Contact history tracking
9. Vendor performance metrics by part age

---

## Current Workaround

Until feature is built, manually review `Open Back Orders - [DATE].txt` file:
- Column 6 = Age in days
- Filter for age >= 5
- Cross-reference with "Back-Ordered" or "On Order" status

**Customers needing calls as of Feb 5, 2026:**
1. ☎️ SNYDER'S LAWNCARE (269) 779-8350 - 37 days
2. ☎️ Generator Service Vehicles (269) 685-9557 - 16 days
3. ☎️ DON KOLUDROVICH (269) 209-0111 - 13 days
4. ☎️ Colleen Ritchie (269) 303-9272 - 8 days
5. ☎️ BRONCO ASPHALT MAINT (269) 384-9816 - 7 days (3 parts)

---

## Files to Modify (When Implementing)

- **Backend:** `/home/ubuntu/shopmgr/app.py`
  - Update `parse_open_back_orders()` function
  - Add age extraction logic
  - Add phone number extraction

- **Frontend:** `/home/ubuntu/shopmgr/templates/dashboard.html`
  - Add age column to parts display
  - Add color coding CSS
  - Create notifications section (Phase 2)

- **Data:** Daily upload of `Open Back Orders - [DATE].txt` (already automated)

---

**Status:** Feature documented, ready for implementation planning  
**Next Steps:** Prioritize in roadmap and schedule development sprint
