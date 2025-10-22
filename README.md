# 🎭 Django Entertainment & Ticket Booking Platform

A complete, production-ready Django-based entertainment platform featuring ticket booking, artist reels, event management, and Paystack payment integration with role-based access control.

## 🌟 Features

### 👥 User Roles

#### 1. Ordinary User
- ✅ Register/Login with email confirmation
- ✅ Browse and search events
- ✅ Book tickets with Paystack
- ✅ Follow artists
- ✅ View and favorite reels
- ✅ Share events to social platforms (WhatsApp, Facebook, Twitter)
- ✅ Upgrade account to Artist or Host
- ✅ View booking history and favorites

#### 2. Artist
- ✅ Upload and manage reels (video/image)
- ✅ View follower statistics
- ✅ Track plays and likes
- ✅ Manage artist profile
- ✅ Can upgrade to Host (dual role)

#### 3. Host
- ✅ Create and manage events
- ✅ Set ticket prices and venue details
- ✅ View bookings and earnings (90% after commission)
- ✅ Event analytics (views, favorites, shares, bookings)
- ✅ Can also be Artist (dual role)

#### 4. Super Admin
- ✅ Full dashboard access
- ✅ Platform analytics (revenue, users, events)
- ✅ Manage users and roles
- ✅ Approve/reject role upgrade requests
- ✅ Transaction monitoring
- ✅ Commission tracking (10% per booking)

### 🎯 Core Features

**Authentication & Authorization**
- Email-based authentication with Django Allauth
- Email confirmation and password reset
- Role-based access control
- Profile management with avatar upload

**Event Management**
- Create events with details (name, description, venue, date, price)
- Upload event images
- Set ticket availability
- Event categories and tags
- Search and filter events

**Booking System**
- Secure ticket booking with Paystack
- Real-time availability checking
- Booking confirmation emails
- Booking history
- QR code tickets (optional)

**Artist Features**
- Upload reels (video/image)
- Reel management dashboard
- Follower system
- View and like tracking
- Artist profile customization

**Social Features**
- Follow/unfollow artists (AJAX)
- Favorite events and reels (AJAX)
- Share events to social platforms
- Share tracking and analytics
- Activity feed

**Payment & Commission**
- Paystack integration
- 10% admin commission on bookings
- Host earnings dashboard
- Transaction history
- Payout management

**Analytics & Reporting**
- Event analytics (views, favorites, shares, bookings)
- Artist stats (followers, plays, likes)
- Platform revenue tracking
- User engagement metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Git
- Paystack account

### Installation

```bash
# 1. Clone repository
git clone https://github.com/br41n7/Tick
cd Tick

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r entertainment_requirements.txt

# 4. Configure environment
cp entertainment_env.example .env
# Edit .env with your Paystack keys

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Create media directories
mkdir -p media/avatars media/reels media/event_images

# 8. Run development server
python manage.py runserver
```

Visit http://localhost:8000

## 📁 Project Structure

```
entertainment-platform/
├── entertainment_project/     # Main Django project
│   ├── settings.py           # Configuration
│   ├── urls.py               # URL routing
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
│
├── accounts/                  # User management & roles
│   ├── models.py             # CustomUser, RoleUpgradeRequest
│   ├── views.py              # Auth, profile, upgrades
│   ├── forms.py              # User forms
│   ├── urls.py               # Account URLs
│   └── admin.py              # Admin configuration
│
├── events/                    # Event management
│   ├── models.py             # Event, Booking, Favorite, Share
│   ├── views.py              # Event CRUD, booking
│   ├── forms.py              # Event forms
│   ├── urls.py               # Event URLs
│   └── admin.py              # Admin configuration
│
├── artists/                   # Artist profiles & reels
│   ├── models.py             # ArtistProfile, Reel, Follow
│   ├── views.py              # Reel upload, following
│   ├── forms.py              # Artist forms
│   ├── urls.py               # Artist URLs
│   └── admin.py              # Admin configuration
│
├── payments/                  # Paystack integration
│   ├── models.py             # Transaction, Commission
│   ├── views.py              # Payment processing
│   ├── paystack.py           # Paystack API wrapper
│   ├── urls.py               # Payment URLs
│   └── admin.py              # Admin configuration
│
├── core/                      # Base templates & dashboard
│   ├── views.py              # Dashboard routing
│   ├── context_processors.py # Global context
│   ├── urls.py               # Core URLs
│   └── templatetags/         # Custom template tags
│
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Landing page
│   ├── accounts/             # Account templates
│   ├── events/               # Event templates
│   ├── artists/              # Artist templates
│   ├── payments/             # Payment templates
│   └── core/                 # Dashboard templates
│
├── static/                    # Static files
│   ├── css/
│   │   └── style.css         # Custom CSS
│   ├── js/
│   │   ├── main.js           # Main JavaScript
│   │   └── ajax.js           # AJAX handlers
│   └── images/               # Static images
│
└── media/                     # User uploads
    ├── avatars/              # User avatars
    ├── reels/                # Artist reels
    └── event_images/         # Event images
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite default, PostgreSQL for production)
# DATABASE_URL=postgresql://user:password@localhost:5432/entertainment_db

# Paystack Configuration
PAYSTACK_PUBLIC_KEY=pk_test_your_key_here
PAYSTACK_SECRET_KEY=sk_test_your_key_here

# Commission Settings
ADMIN_COMMISSION_RATE=0.10  # 10%

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Site Configuration
SITE_NAME=Entertainment Platform
SITE_URL=http://localhost:8000
```

### Paystack Setup

1. Create account at https://paystack.com
2. Get API keys from dashboard
3. Add keys to `.env` file
4. Configure webhook: `https://yourdomain.com/payments/webhook/`
5. Test with Paystack test cards

**Test Cards:**
- Success: `4084084084084081`
- Insufficient Funds: `4084080000000408`

## 💳 Payment Flow

1. User selects event and clicks "Book Ticket"
2. System checks ticket availability
3. Redirects to Paystack checkout
4. User completes payment
5. Paystack webhook confirms payment
6. Booking created in database
7. Commission calculated (10% admin, 90% host)
8. Confirmation email sent
9. Ticket available in user dashboard

## 🎨 Key Features Implementation

### Role Upgrade System

Users can upgrade their role from Settings:

```python
# User requests upgrade
upgrade_request = RoleUpgradeRequest.objects.create(
    user=request.user,
    request_type='to_artist',  # or 'to_host'
    reason='I want to share my music with the world'
)

# Admin approves
upgrade_request.approve(admin_user)

# User role updated automatically
user.is_artist = True  # or is_host = True
```

### AJAX Features

**Follow/Unfollow Artist:**
```javascript
$.ajax({
    url: '/artists/follow/' + artistId + '/',
    method: 'POST',
    success: function(data) {
        // Update UI
        updateFollowButton(data.is_following);
    }
});
```

**Favorite Event:**
```javascript
$.ajax({
    url: '/events/favorite/' + eventId + '/',
    method: 'POST',
    success: function(data) {
        // Update UI
        updateFavoriteButton(data.is_favorite);
    }
});
```

### Social Sharing

Events include share buttons for:
- WhatsApp: Pre-filled message with event details
- Facebook: Share with event image and description
- Twitter: Tweet with hashtags and event link

Share counts tracked per event for analytics.

## 📊 Database Models

### Key Models

**CustomUser**
- Extended Django user with roles
- Fields: email, role, is_artist, is_host, avatar, bio
- Methods: upgrade_to_artist(), upgrade_to_host(), can_create_events()

**Event**
- Event details and management
- Fields: title, description, venue, date, price, tickets_available
- Relations: host (User), bookings, favorites, shares

**Booking**
- Ticket bookings with payment
- Fields: user, event, quantity, total_amount, payment_status
- Relations: transaction

**Reel**
- Artist content uploads
- Fields: artist, title, media_file, media_type (video/image)
- Relations: views, likes

**Transaction**
- Payment records
- Fields: user, amount, commission_amount, paystack_reference
- Relations: booking

## 🎯 User Dashboards

### Ordinary User Dashboard
- Upcoming bookings
- Favorite events
- Favorite reels
- Followed artists
- Quick actions (browse events, discover artists)

### Artist Dashboard
- Upload new reel
- Manage reels
- Follower statistics
- View counts and likes
- Recent activity

### Host Dashboard
- Create new event
- Manage events
- Booking statistics
- Earnings report
- Event analytics

### Dual Role Dashboard (Artist + Host)
- Combined features from both dashboards
- Unified analytics
- Quick switcher between modes

### Admin Dashboard
- Platform statistics
- User management
- Role upgrade requests
- Transaction monitoring
- Revenue analytics

## 🚀 Deployment

### Render.com Deployment

1. **Prepare Repository**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Render Account**
- Sign up at https://render.com
- Connect GitHub repository

3. **Create PostgreSQL Database**
- New → PostgreSQL
- Name: entertainment_db
- Note the connection string

4. **Create Web Service**
- New → Web Service
- Connect repository
- Configure:
  - Build Command: `./build.sh`
  - Start Command: `gunicorn entertainment_project.wsgi:application`

5. **Set Environment Variables**
```
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<from-postgresql-service>
PAYSTACK_PUBLIC_KEY=<your-key>
PAYSTACK_SECRET_KEY=<your-key>
ADMIN_COMMISSION_RATE=0.10
```

6. **Deploy**
- Click "Create Web Service"
- Wait for deployment
- Visit your app URL

## 📱 Responsive Design

- Mobile-first Bootstrap 5 design
- Touch-friendly interfaces
- Responsive navigation
- Optimized images
- Fast loading times

## 🔒 Security

- CSRF protection on all forms
- SQL injection prevention
- XSS protection
- Secure password hashing (PBKDF2)
- HTTPS enforcement (production)
- Secure file uploads
- Payment security via Paystack
- Role-based access control

## 📈 Analytics

### Event Analytics
- Total views
- Favorites count
- Share count (by platform)
- Booking count
- Revenue generated
- Conversion rate

### Artist Analytics
- Total followers
- Reel views
- Reel likes
- Engagement rate
- Growth trends

### Platform Analytics (Admin)
- Total users (by role)
- Total events
- Total bookings
- Total revenue
- Commission earned
- Top events
- Top artists
- Revenue trends

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test events
python manage.py test artists
python manage.py test payments

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📚 API Endpoints

### Events
- `GET /events/` - List all events
- `GET /events/<id>/` - Event detail
- `POST /events/create/` - Create event (Host only)
- `POST /events/<id>/book/` - Book ticket
- `POST /events/<id>/favorite/` - Toggle favorite
- `POST /events/<id>/share/` - Track share

### Artists
- `GET /artists/` - List all artists
- `GET /artists/<id>/` - Artist profile
- `POST /artists/<id>/follow/` - Toggle follow
- `GET /artists/reels/` - List reels
- `POST /artists/reels/upload/` - Upload reel
- `POST /artists/reels/<id>/like/` - Toggle like

### Payments
- `POST /payments/initialize/` - Initialize payment
- `POST /payments/webhook/` - Paystack webhook
- `GET /payments/verify/<reference>/` - Verify payment

### Accounts
- `POST /user/upgrade/` - Request role upgrade
- `GET /user/profile/` - View profile
- `POST /user/profile/update/` - Update profile

## 🛠️ Development

### Adding New Features

1. **Create Model**
```python
# In appropriate app's models.py
class NewFeature(models.Model):
    # Define fields
    pass
```

2. **Create Migration**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Views**
```python
# In views.py
def new_feature_view(request):
    # Implement logic
    pass
```

4. **Add URLs**
```python
# In urls.py
path('new-feature/', views.new_feature_view, name='new_feature'),
```

5. **Create Template**
```html
<!-- In templates/ -->
{% extends 'base.html' %}
{% block content %}
<!-- Your content -->
{% endblock %}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file

## 🆘 Support

- **Documentation**: See this README
- **Issues**: GitHub Issues
- **Email**: iyanuolalegan1@gmail.com

- Django framework
- Bootstrap 5
- Paystack
- All contributors

## 📞 Contact

For questions or support:
- Email: iyanuolalegan1@gmail.com
- GitHub: @br41n7
- WA: https://wa.me/+2349118263860

---

**Built with ❤️ using Django**

**Status**: ✅ Not Ready# Tick
