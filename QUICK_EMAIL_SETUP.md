# Quick Email Setup Guide

## Option 1: Using Gmail (Recommended for Testing)

### Step 1: Get Gmail App Password
1. Go to your Google Account: https://myaccount.google.com/
2. Enable **2-Factor Authentication** (Security → 2-Step Verification)
3. Go to **App Passwords**: https://myaccount.google.com/apppasswords
4. Generate a new app password for "Mail"
5. **Copy the 16-character password** (you'll need it in Step 3)

### Step 2: Create `.env` File
Create a file named `.env` in your project root (`d:/StockMaster/.env`):

```env
USE_SMTP_EMAIL=true
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
MANAGER_EMAIL=your-actual-email@gmail.com
```

**Replace:**
- `your-actual-email@gmail.com` with your Gmail address
- `your-16-char-app-password` with the app password from Step 1

### Step 3: Install python-dotenv
```bash
pip install python-dotenv
```

### Step 4: Update settings.py
Add this at the very top of `StockMaster/settings.py` (after imports):

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
```

### Step 5: Restart Server
```bash
# Stop the current server (Ctrl+C)
python manage.py runserver
```

### Step 6: Test It!
1. Go to Products → Add a product with min stock = 50
2. Use "Quick Stock In" to add 30 units (below minimum)
3. **Check your email inbox!** 📧

---

## Option 2: Using Other Email Providers

### For Outlook/Hotmail:
```env
USE_SMTP_EMAIL=true
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
MANAGER_EMAIL=your-email@outlook.com
```

### For Yahoo:
```env
USE_SMTP_EMAIL=true
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@yahoo.com
EMAIL_HOST_PASSWORD=your-app-password
MANAGER_EMAIL=your-email@yahoo.com
```

---

## Troubleshooting

### "SMTPAuthenticationError"
- Double-check your email and password
- For Gmail, make sure you're using the **App Password**, not your regular password
- Verify 2FA is enabled

### "Connection refused"
- Check your firewall settings
- Verify EMAIL_HOST and EMAIL_PORT are correct

### Email not received?
- Check spam folder
- Verify MANAGER_EMAIL is correct
- Check server terminal for error messages

---

## Quick Test Command

After setup, run:
```bash
python test_email_alert.py
```

You should receive an email at the MANAGER_EMAIL address!

---

**Security Note:** Never commit your `.env` file to Git! It's already in `.gitignore`.
