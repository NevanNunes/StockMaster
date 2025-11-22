# Email Configuration Guide for StockMaster

## Current Setup (Development)

The email feature is currently configured to print emails to the **console/terminal** instead of sending them via SMTP.

### Configuration in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@stockmaster.com'
MANAGER_EMAIL = 'manager@stockmaster.com'
```

---

## How to Test the Email Feature

### Method 1: Via the UI (Recommended)

1. **Create a Product with Low Stock Level:**
   - Go to Products → Add Product
   - Set "Minimum Stock Level" to 50

2. **Add Stock Below Minimum:**
   - Use "Quick Stock In" modal
   - Add quantity less than 50 (e.g., 30)

3. **Check the Terminal:**
   - Look at the terminal where `python manage.py runserver` is running
   - You should see the email printed there

### Method 2: Via Python Script

Run the test script:
```bash
python test_email_alert.py
```

The email will be printed to the console.

---

## Email Triggers

Low stock alerts are sent when:
1. Stock quantity **decreases** to or below `min_stock_level`
2. No active alert already exists for that product/location

The email includes:
- Product name and SKU
- Current quantity vs minimum level
- Location and warehouse
- Warning message

---

## Production Configuration

To send real emails in production, update `settings.py`:

### For Gmail:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
MANAGER_EMAIL = 'manager@yourcompany.com'
```

### For Other SMTP Providers:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yourprovider.com'
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'your-smtp-username'
EMAIL_HOST_PASSWORD = 'your-smtp-password'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'
MANAGER_EMAIL = 'manager@yourcompany.com'
```

---

## Testing Real Email Sending

1. Update `settings.py` with your SMTP credentials
2. Restart the Django server
3. Trigger a low stock alert
4. Check the `MANAGER_EMAIL` inbox

---

## Troubleshooting

### Email not appearing in console?
- Make sure you're looking at the terminal where `manage.py runserver` is running
- Check that stock is actually below minimum level
- Verify no active alert already exists for that product/location

### Gmail App Password Setup:
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account → Security → App Passwords
3. Generate an app password for "Mail"
4. Use this password in `EMAIL_HOST_PASSWORD`

---

## Example Email Output

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: =?utf-8?b?4pqg77iPIExvdyBTdG9jayBBbGVydDogVGVzdCBQcm9kdWN0IGZvciBFbWFpbCAoVEVTVC1FTUFJTC0wMDEp?=
From: noreply@stockmaster.com
To: manager@stockmaster.com
Date: Fri, 22 Nov 2024 08:00:00 -0000

Low Stock Alert

Product: Test Product for Email
SKU: TEST-EMAIL-001
Location: Receiving Area (Main Warehouse)
Current Quantity: 30 pcs
Minimum Level: 50 pcs

⚠️ Stock is below minimum level. Please reorder immediately.

---
StockMaster Inventory Management System
```

---

**Note**: In development mode, emails are only printed to console. Switch to SMTP backend for production use.
