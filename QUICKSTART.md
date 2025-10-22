# 🚀 Quick Start Guide - Entertainment Platform

Get the Django Entertainment & Ticket Booking Platform running in 10 minutes!

## ⚡ Prerequisites

- Python 3.11+
- pip
- Git
- Paystack account (for payments)

## 📦 Installation Steps

### Step 1: Clone and Setup (2 minutes)

```bash
# Clone repository
git clone https://github.com/Br41n7/Tick
cd Tick

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r entertainment_requirements.txt
```

### Step 2: Configure Environment (2 minutes)

```bash
# Copy environment template
cp entertainment_env.example .env
```

Edit `.env` file with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Paystack (get from https://paystack.com)
PAYSTACK_PUBLIC_KEY=pk_test_your_key
PAYSTACK_SECRET_KEY=sk_test_your_key

# Commission rate (10% default)
ADMIN_COMMISSION_RATE=0.10
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Setup Database (2 minutes)

```bash
# Run migrations
python entertainment_manage.py migrate

# Create superuser (admin)
python entertainment_manage.py createsuperuser
# Enter email, username, and password

# Create media directories
mkdir -p media/avatars media/reels media/event_images
mkdir -p static staticfiles
```

### Step 4: Run Server (1 minute)

```bash
# Start development server
python entertainment_manage.py runserver
```

🎉 **Done!** Visit http://localhost:8000

## 🎯 First Steps

### 1. Access the Platform

Open your browser:
- **Home**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Sign Up**: http://localhost:8000/accounts/signup/

### 2. Login as Admin

1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Explore the admin dashboard

### 3. Create Test Users

**Option A: Via Admin Panel**
1. Go to Users section
2. Click "Add User"
3. Create users with different roles

**Option B: Via Django Shell**
```bash
python entertainment_manage.py shell
```

```python
from accounts.models import CustomUser

# Create ordinary user
user = CustomUser.objects.create_user(
    email='user@example.com',
    username='testuser',
    password='password123',
    first_name='Test',
    last_name='User'
)

# Create artist
artist = CustomUser.objects.create_user(
    email='artist@example.com',
    username='testartist',
    password='password123',
    first_name='Test',
    last_name='Artist'
)
artist.upgrade_to_artist()

# Create host
host = CustomUser.objects.create_user(
    email='host@example.com',
    username='testhost',
    password='password123',
    first_name='Test',
    last_name='Host'
)
host.upgrade_to_host()
```

### 4. Test User Flows

#### As Ordinary User:
1. Sign up at `/accounts/signup/`
2. Browse events at `/events/`
3. View artist reels at `/artists/`
4. Request role upgrade in Settings

#### As Artist:
1. Login with artist account
2. Go to Dashboard
3. Upload a reel
4. View your stats

#### As Host:
1. Login with host account
2. Go to Dashboard
3. Create an event
4. View bookings and earnings

#### As Admin:
1. Login to admin panel
2. Approve role upgrade requests
3. View platform analytics
4. Manage users and events

## 🎨 Key Features to Test

### 1. Event Booking Flow

```
1. Browse events → 2. Click event → 3. Click "Book Ticket"
→ 4. Enter quantity → 5. Pay with Paystack → 6. Booking confirmed
```

**Test Card (Paystack):**
- Card: `4084084084084081`
- Expiry: Any future date
- CVV: `408`

### 2. Role Upgrade System

```
1. Login as user → 2. Go to Settings → 3. Request upgrade
→ 4. Admin approves → 5. User gets new role
```

### 3. Follow/Unfollow Artists

```
1. Browse artists → 2. Click artist profile → 3. Click "Follow"
→ 4. See follower count update (AJAX)
```

### 4. Favorite Events

```
1. Browse events → 2. Click heart icon → 3. Event added to favorites
→ 4. View in "My Favorites"
```

### 5. Share Events

```
1. View event → 2. Click share button (WhatsApp/Facebook/Twitter)
→ 3. Share tracked → 4. Count updated
```

## 📊 Sample Data

### Create Sample Events (Django Shell)

```python
from accounts.models import CustomUser
from events.models import Event
from datetime import datetime, timedelta

# Get a host user
host = CustomUser.objects.filter(is_host=True).first()

# Create sample event
event = Event.objects.create(
    host=host,
    title='Summer Music Festival 2024',
    description='Join us for an amazing night of music!',
    category='festival',
    venue='Central Park',
    address='123 Park Avenue, City',
    event_date=datetime.now() + timedelta(days=30),
    duration_hours=6,
    ticket_price=50.00,
    tickets_available=500
)
```

### Create Sample Reels (Django Shell)

```python
from artists.models import ArtistProfile, Reel

# Get or create artist profile
artist_user = CustomUser.objects.filter(is_artist=True).first()
profile, created = ArtistProfile.objects.get_or_create(
    user=artist_user,
    defaults={
        'stage_name': 'DJ Test',
        'genre': 'Electronic',
        'bio': 'Professional DJ and producer'
    }
)

# Note: You'll need to upload actual media files
# This is just for structure demonstration
```

## 🔧 Common Commands

```bash
# Run server
python entertainment_manage.py runserver

# Make migrations
python entertainment_manage.py makemigrations

# Apply migrations
python entertainment_manage.py migrate

# Create superuser
python entertainment_manage.py createsuperuser

# Collect static files
python entertainment_manage.py collectstatic

# Django shell
python entertainment_manage.py shell

# Run tests
python entertainment_manage.py test
```

## 🎯 Project Structure Overview

```
entertainment-platform/
├── accounts/          # User management & roles
├── events/           # Event management & booking
├── artists/          # Artist profiles & reels
├── payments/         # Paystack integration
├── core/             # Dashboards & base templates
├── templates/        # HTML templates
├── static/          # CSS, JS, images
└── media/           # User uploads
```

## 🔑 Key URLs

### Public URLs
- Home: `/`
- Events: `/events/`
- Event Detail: `/events/<slug>/`
- Artists: `/artists/`
- Artist Profile: `/artists/<id>/`

### User URLs
- Dashboard: `/dashboard/`
- Profile: `/user/profile/`
- Settings: `/user/settings/`
- My Bookings: `/events/my-bookings/`
- My Favorites: `/events/my-favorites/`

### Artist URLs
- Upload Reel: `/artists/reels/upload/`
- My Reels: `/artists/reels/my-reels/`
- Artist Stats: `/artists/stats/`

### Host URLs
- Create Event: `/events/create/`
- My Events: `/events/my-events/`
- Earnings: `/payments/earnings/`

### Admin URLs
- Admin Panel: `/admin/`
- Analytics: `/admin/analytics/`

## 💡 Tips & Tricks

### 1. Quick User Role Changes

```python
# In Django shell
from accounts.models import CustomUser

user = CustomUser.objects.get(email='user@example.com')
user.upgrade_to_artist()  # Make artist
user.upgrade_to_host()    # Make host (can have both)
```

### 2. Reset Database

```bash
# Delete database
rm db.sqlite3

# Delete migrations (optional)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate
python entertainment_manage.py migrate
python entertainment_manage.py createsuperuser
```

### 3. Test Paystack Locally

Use Paystack test mode:
- Test cards: https://paystack.com/docs/payments/test-payments
- Webhook testing: Use ngrok or Paystack CLI

### 4. Debug Mode

In `.env`:
```env
DEBUG=True  # Shows detailed errors
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
python entertainment_manage.py runserver 8001
```

### Static Files Not Loading
```bash
python entertainment_manage.py collectstatic --clear
```

### Database Errors
```bash
python entertainment_manage.py migrate --run-syncdb
```

### Import Errors
```bash
pip install -r entertainment_requirements.txt --force-reinstall
```

## 📚 Next Steps

1. **Read Full Documentation**
   - [ENTERTAINMENT_README.md](ENTERTAINMENT_README.md)
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
   - [ENTERTAINMENT_PROJECT_SUMMARY.md](ENTERTAINMENT_PROJECT_SUMMARY.md)

2. **Customize the Platform**
   - Add your branding
   - Customize colors and styles
   - Add more event categories

3. **Deploy to Production**
   - Follow deployment guide
   - Set up PostgreSQL
   - Configure Paystack webhooks

4. **Add More Features**
   - Email notifications
   - SMS reminders
   - QR code tickets
   - Advanced analytics

## 🆘 Getting Help

- **Documentation**: See README files
- **Issues**: Create GitHub issue
- **Email**: support@example.com

## 🎉 You're Ready!

The platform is now running. Start exploring and testing all features!

**Test Accounts:**
- Admin: Your superuser credentials
- User: user@example.com / password123
- Artist: artist@example.com / password123
- Host: host@example.com / password123

**Happy coding! 🚀**

---

For detailed implementation, see [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

For deployment, see [ENTERTAINMENT_DEPLOYMENT.md](ENTERTAINMENT_DEPLOYMENT.md)