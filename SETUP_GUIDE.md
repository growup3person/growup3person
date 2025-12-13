# 📋 Complete Setup Guide - Pura Project Configuration

## 🔍 Current Project Structure
```
employee-system/
├── app.py                 ✅ (ready - reads DATABASE_URL + SECRET_KEY from env)
├── database.py            ✅ (ready - SQLAlchemy models)
├── requirements.txt       ✅ (has gunicorn for deployment)
├── Procfile              ✅ (for Render/Railway/Heroku)
├── .env.example          ✅ (template env file)
├── README.md             ✅ (basic info)
├── .env                  ❌ CREATE THIS (local testing)
├── static/
│   ├── script.js         ⚠️ CHANGE API_URL (line 1)
│   └── style.css         ✅ (no changes)
└── templates/
    └── index.html        ✅ (no changes)
```

---

## 1️⃣ LOCAL SETUP - अपने Computer पर चलाने के लिए

### Step 1: Create `.env` file

**File: `.env`** (create करो project folder में)

```env
DATABASE_URL=sqlite:///referral_system.db
SECRET_KEY=my-super-secret-key-12345
```

**या अगर Supabase Postgres use करना है:**

```env
DATABASE_URL=postgresql://postgres.xxxxx:password@db.supabase.co:5432/postgres
SECRET_KEY=my-super-secret-key-12345
```

---

### Step 2: Install dependencies

Terminal में चलाओ:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

---

### Step 3: Run locally

```powershell
python app.py
```

Output देखेगा:
```
✅ Database tables created successfully
✅ Admin created successfully
📧 Email: admin@example.com
🔑 Password: admin123
🆔 Admin ID: USER1A2B3C4D5
 * Running on http://127.0.0.1:5000
```

- Open browser: `http://localhost:5000`
- Login करो:
  - Email: `admin@example.com`
  - Password: `admin123`

---

## 2️⃣ PRODUCTION SETUP - Server पर Deploy करने के लिए

### Option A: Render.com (Recommended - Free)

#### Step 1: Prepare project for Git

Terminal में:
```powershell
git add .
git commit -m "Initial commit - employee system"
git push
```

#### Step 2: Go to Render.com

1. https://render.com पर signup करो (free)
2. Click "New +" → "Web Service"
3. Connect GitHub account → select repo

#### Step 3: Fill deployment form

```
Name: employee-system
Environment: Python 3.11
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

#### Step 4: Set Environment Variables

Dashboard में "Environment" tab क्लिक करो और add करो:

```
DATABASE_URL=postgresql://postgres.xxxxx:password@db.supabase.co:5432/postgres
SECRET_KEY=some-random-secure-string-here
```

(Connection string Supabase से लो)

#### Step 5: Deploy

Click "Create Web Service" → Wait 2-3 min → Live URL मिलेगा like:
```
https://employee-system-xxxxx.onrender.com
```

---

### Option B: Railway.app (Alternative)

1. https://railway.app पर signup करो
2. Click "New Project" → "Deploy from GitHub"
3. Select repo
4. Railway automatically detects Python + Procfile
5. Set variables same as above
6. Deploy → Live link मिलेगा

---

### Option C: Heroku (Paid - बेहतर reliability)

1. https://heroku.com पर signup करो
2. Download Heroku CLI
3. Terminal में:
```powershell
heroku login
git push heroku main
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=...
```

---

## 3️⃣ FRONTEND CONFIGURATION - API URLs Set करना

### File: `static/script.js` - Line 1 को change करो

**अगर Local testing कर रहे हो:**
```javascript
const API_URL = 'http://localhost:5000/api';
```

**अगर Production में हो (Render):**
```javascript
const API_URL = 'https://employee-system-xxxxx.onrender.com/api';
```

**अगर Production में हो (Railway):**
```javascript
const API_URL = 'https://employee-system-production.up.railway.app/api';
```

**अगर Frontend + Backend same Flask server से serve हो (सबसे simple):**
```javascript
const API_URL = '/api';
```

---

## 4️⃣ DATABASE SETUP - Cloud Postgres (Supabase)

### Create Free Supabase Project

1. https://supabase.com signup करो (free tier available)
2. Create new project → Select region
3. Wait for setup (~2 min)
4. Go to Settings → Database
5. Copy connection string (like `postgresql://postgres.xxxxx:...`)
6. Paste को `.env` में या deployment env में `DATABASE_URL` के लिए

**App automatically create करेगा सभी tables पहली बार run करने पर।**

---

## 5️⃣ BACKEND API ENDPOINTS - क्या काम करता है

| Method | Endpoint | Auth | Input | Output |
|--------|----------|------|-------|--------|
| POST | `/api/signup` | ❌ | name, email, password, referralId, referrerName | {message, userId} |
| POST | `/api/login` | ❌ | email, password | {token, user} |
| GET | `/api/verify` | ✅ Token | - | {user} |
| GET | `/api/users` | ✅ Admin | - | {users, totalUsers, todayUsers} |
| GET | `/api/referrals/:id` | ✅ Admin | user_id param | {user, referrals} |
| GET | `/api/qrcode` | ❌ | - | {qrCode} |
| POST | `/api/qrcode` | ✅ Admin | {qrCode: base64} | {message} |
| DELETE | `/api/qrcode` | ✅ Admin | - | {message} |

**Auth header format:**
```
Authorization: Bearer <token_from_login>
```

---

## 6️⃣ ENVIRONMENT VARIABLES - सभी जगह set करने हैं

### Local Testing (`.env` file):
```env
DATABASE_URL=sqlite:///referral_system.db
SECRET_KEY=local-test-key-123
```

### Production (Deployment dashboard - Render/Railway/Heroku):
```
DATABASE_URL=postgresql://postgres.xxxxx:password@db.supabase.co:5432/postgres
SECRET_KEY=some-very-secure-random-string-here
PORT=5000 (auto-set by platform)
```

**SECRET_KEY generate करने के लिए:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 7️⃣ FRONTEND FUNCTIONALITY - क्या करता है

### Login Page
- Email + Password enter करो
- Server से token मिलता है
- Token localStorage में store होता है
- अगर admin है तो admin dashboard खुलता है
- अगर normal user है तो home page खुलता है

### User Home Page
- अपनी information दिख जाती है (name, email, referral ID)
- QR code दिखता है (अगर admin ने upload किया हो)
- Share करने के लिए referral ID use कर सकते हो

### Admin Dashboard
- सभी users की list दिख जाती है
- हर user के referrals देख सकते हो
- QR code upload/delete कर सकते हो
- Total users + Today's users count दिख जाता है
- Search functionality है users को find करने के लिए

### Signup/Referral System
- नया user referral ID से signup कर सकता है
- Admin ke through या किसी existing user ke through signup हो सकता है
- हर user ko unique ID मिलता है (USER123ABC...)

---

## 8️⃣ COMPLETE EXAMPLE WORKFLOW

### Local Testing:

```powershell
# 1. Create .env file
echo "DATABASE_URL=sqlite:///referral_system.db" > .env
echo "SECRET_KEY=local-test-secret" >> .env

# 2. Create virtual environment
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

# 3. Install packages
pip install -r requirements.txt

# 4. Run app
python app.py

# 5. Open browser
# http://localhost:5000

# 6. Login
# Email: admin@example.com
# Password: admin123

# 7. Create new users via signup
# या as admin add कर सकते हो
```

### Production Deployment (Render):

```powershell
# 1. Update script.js API_URL
# Change line 1 to: const API_URL = 'https://employee-system-xxxxx.onrender.com/api';

# 2. Commit changes
git add .
git commit -m "Update API URL for production"
git push

# 3. Go to Render dashboard
# - New Web Service
# - Connect GitHub repo
# - Set environment variables
# - Click Deploy

# 4. Wait 2-3 minutes
# https://employee-system-xxxxx.onrender.com live होगा

# 5. Share with users!
```

---

## 9️⃣ FILES - क्या change करना है, क्या नहीं

### ✅ NO CHANGES NEEDED:
- `app.py` — पहले से env vars read करता है
- `database.py` — तैयार है
- `requirements.txt` — सब packages हैं
- `Procfile` — deployment के लिए ready है
- `templates/index.html` — HTML form तैयार है
- `static/style.css` — styling complete है
- `.env.example` — template है

### ⚠️ YOU MUST CREATE/CHANGE:

1. **Create `.env`** (local testing के लिए)
   - File में डालो: `DATABASE_URL` और `SECRET_KEY`

2. **Update `static/script.js` line 1**
   - Change `const API_URL = ...` अपने backend URL से

3. **Set deployment env vars**
   - Render/Railway dashboard में `DATABASE_URL` + `SECRET_KEY`

---

## 🔟 COMPLETE CHECKLIST - Production Deploy से पहले

- [ ] `.env` file create किया locally
- [ ] `pip install -r requirements.txt` चलाया
- [ ] `python app.py` से local test किया
- [ ] `http://localhost:5000` पर login काम करता है
- [ ] सभी code को GitHub पर push किया
- [ ] Render/Railway account बनाया
- [ ] Web Service create किया
- [ ] `DATABASE_URL` + `SECRET_KEY` environment में set किए
- [ ] Deployment complete है
- [ ] Live URL मिल गया (जैसे `https://employee-system-xxxxx.onrender.com`)
- [ ] `static/script.js` line 1 update किया with production URL
- [ ] Production पर login test किया
- [ ] Users को live link share किया

---

## 1️⃣1️⃣ TROUBLESHOOTING

### Q: Database connection fail हो रहा है?
**A:** 
- `.env` में `DATABASE_URL` check करो
- Supabase से सही connection string copy किया?
- Typo या extra spaces तो नहीं हैं?

### Q: Login काम नहीं कर रहा?
**A:**
- Browser console खोलो (F12)
- Network tab में देको क्या error आ रहा है
- `static/script.js` में `API_URL` सही है क्या?
- Backend logs देखो क्या error है

### Q: Admin नहीं बन रहा?
**A:**
- अगर sqlite use कर रहे हो तो delete करो `referral_system.db`
- फिर `python app.py` दोबारा चलाओ
- Admin automatically create होगा

### Q: CORS errors आ रहे हैं?
**A:**
- `static/script.js` में `/api` use करो (same server से serve करो)
- या `API_URL` को सही deployed URL से update करो
- Flask-CORS पहले से enabled है

### Q: PORT already in use है?
**A:**
```powershell
# Different port पर चलाओ
python app.py --port 5001
```

### Q: Deploy के बाद blank page दिख रहा है?
**A:**
- Platform logs देखो (Render → Logs)
- Environment variables set हैं क्या?
- Frontend में API_URL सही है क्या?

---

## 1️⃣2️⃣ IMPORTANT NOTES

1. **Security**
   - `SECRET_KEY` को secure value से change करो production में
   - Passwords hashed हैं (pbkdf2:sha256)
   - Tokens JWT से validate होते हैं

2. **Database**
   - SQLAlchemy automatically सभी tables create करता है
   - Migrations की जरूरत नहीं (यह simple system है)
   - Cloud Postgres recommend किया है reliability के लिए

3. **Scalability**
   - Multiple users एक साथ use कर सकते हैं
   - Cloud Postgres unlimited connections support करता है
   - Procfile में 3 workers configured हैं

4. **Frontend & Backend**
   - Frontend static HTML/CSS/JS है
   - Backend Python Flask है
   - दोनों same या different server पर हो सकते हैं
   - CORS enabled है cross-origin के लिए

---

## 1️⃣3️⃣ WHAT'S INCLUDED

✅ User signup via referral system
✅ User login with JWT tokens
✅ Admin dashboard with all users list
✅ Referral tree visualization
✅ QR code upload/management (for marketing)
✅ User search functionality
✅ Statistics (total users, today's users)
✅ Cloud database support (PostgreSQL)
✅ Production-ready deployment (Render/Railway)
✅ CORS enabled for flexibility
✅ Password hashing & JWT auth
✅ Mobile-responsive frontend

---

**Ab ready ho? Local test करो या directly deploy करna है?**
