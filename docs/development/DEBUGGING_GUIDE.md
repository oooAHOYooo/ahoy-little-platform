# Debugging Guide: How to Check Server Logs

## 🔍 In Chrome DevTools (Client-Side)

### 1. **Network Tab** - See API Requests/Responses
1. Open Chrome DevTools: `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
2. Click the **Network** tab
3. Filter by **Fetch/XHR** to see only API calls
4. Look for failed requests (red status codes like 500)
5. Click on a request to see:
   - **Headers**: Request and response headers
   - **Preview/Response**: The actual error message from server
   - **Status**: HTTP status code (500 = server error)

### 2. **Console Tab** - See JavaScript Errors
1. Open Chrome DevTools
2. Click the **Console** tab
3. Look for red error messages
4. Filter by "Error" or "Failed" using the filter box

### Example: Checking Login Error
1. Open DevTools → Network tab
2. Try to log in
3. Find the `/api/auth/login` request (should be red if it failed)
4. Click it → Go to **Response** tab
5. You'll see the error message like:
   ```json
   {
     "error": "login_failed",
     "message": "An error occurred during login. Please try again."
   }
   ```

---

## 🖥️ Server Logs (Terminal/Console)

**Important**: Chrome shows client-side logs. Server logs appear in the terminal where you started the server.

### If Running Locally:

#### Option 1: Flask Dev Server
```bash
python app.py
# or
python cli.py
```
**Logs appear directly in the terminal** where you ran the command.

#### Option 2: Gunicorn (via script)
```bash
./scripts/migrate_and_start.sh
```
**Logs appear in the terminal** where you ran the script.

#### Option 3: Using dev.py
```bash
python dev.py
```
**Logs appear in the terminal** where you ran the command.

### What to Look For:

When you see a 500 error in Chrome, check your terminal for:
```
ERROR: Login failed
Traceback (most recent call last):
  File "blueprints/api/auth.py", line 287, in login
    login_user(user, remember=True)
  ...
```

### Enable More Verbose Logging:

Add this to see more details:
```python
# In your terminal, set:
export LOG_LEVEL=DEBUG
export FLASK_ENV=development
```

Then restart your server.

---

## 🐛 Quick Debugging Steps

### Step 1: Check Chrome Network Tab
1. Open DevTools → Network
2. Try the failing action (login, etc.)
3. Find the failed request (red)
4. Check the **Response** tab for error details

### Step 2: Check Terminal/Server Logs
1. Look at the terminal where your server is running
2. Find the error traceback
3. Look for lines like:
   - `current_app.logger.exception("Login failed")`
   - `Traceback (most recent call last):`

### Step 3: Check Specific Endpoints

For login errors, the server logs will show:
```
Login failed
Traceback...
```

For username-available errors:
```
Username availability check failed
Traceback...
```

---

## 📝 Common Error Patterns

### 500 Internal Server Error
- **In Chrome**: Check Network tab → Response tab for error message
- **In Terminal**: Look for Python traceback showing the actual exception

### "Illegal invocation" Error
- This is a **client-side** JavaScript error
- Check Console tab in Chrome DevTools
- Usually means a method was called without proper context (like `localStorage.setItem`)

### Database Connection Errors
- Check terminal for database connection errors
- Look for: `OperationalError`, `ConnectionError`, or database URL issues

---

## 💡 Pro Tips

1. **Keep both open**: Chrome DevTools (Network tab) + Terminal (server logs)
2. **Filter in Network tab**: Type `/api/auth` to see only auth-related requests
3. **Preserve log**: Check "Preserve log" in Network tab to keep requests after page reload
4. **Copy as cURL**: Right-click request → Copy → Copy as cURL (to test in terminal)

---

## 🔧 Testing API Endpoints Directly

You can also test endpoints directly using curl:

```bash
# Test login endpoint
curl -X POST http://127.0.0.1:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com","password":"test123"}' \
  -v

# Test username availability
curl "http://127.0.0.1:5001/api/auth/username-available?username=testuser" \
  -v
```

The `-v` flag shows verbose output including response headers and status codes.
