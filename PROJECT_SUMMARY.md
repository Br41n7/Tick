# Django Entertainment & Ticket Booking Platform

## 🎯 Project Overview

A complete Django-based entertainment platform with ticket booking, artist reels, event management, and Paystack payment integration.

## 📋 Features Implemented

### User Roles & Permissions
1. **Ordinary User**
   - Register/Login with email confirmation
   - View and book events
   - Follow artists
   - View and favorite reels
   - Share events to social platforms
   - Upgrade to Artist or Host
   - View booking history

2. **Artist**
   - Upload and manage reels (video/image)
   - View follower stats
   - View plays and likes
   - Can upgrade to Host (dual role)

3. **Host**
   - Create and manage events
   - Set ticket prices and venue details
   - View bookings and earnings
   - Event analytics (favorites, shares)

4. **Super Admin**
   - Full dashboard access
   - Analytics (top events, artists, revenue)
   - Manage users and roles
   - Transaction management

### Core Features
- ✅ Email-based authentication with confirmation
- ✅ Password reset functionality
- ✅ Role upgrade system (User → Artist/Host)
- ✅ Event creation and management
- ✅ Ticket booking with Paystack
- ✅ 10% admin commission on bookings
- ✅ Artist reel uploads (video/image)
- ✅ Follow/unfollow system
- ✅ Favorite events and reels
- ✅ Social sharing (WhatsApp, Facebook, Twitter)
- ✅ Share tracking
- ✅ Booking history
- ✅ Earnings dashboard
- ✅ Analytics and reporting

### AJAX Features
- Real-time booking
- Follow/unfollow without reload
- Favorite/unfavorite events and reels
- Share counter tracking
- Role upgrade requests

## 🏗️ Project Structure

```
entertainment-platform/
├── entertainment_project/     # Main project
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                  # User management & roles
│   ├── models.py             # CustomUser, RoleUpgradeRequest
│   ├── views.py              # Auth, profile, upgrades
│   ├── urls.py
│   └── admin.py
├── events/                    # Event management
│   ├── models.py             # Event, Booking, Favorite, Share
│   ├── views.py              # Event CRUD, booking
│   ├── urls.py
│   └── admin.py
├── artists/                   # Artist profiles & reels
│   ├── models.py             # ArtistProfile, Reel, Follow
│   ├── views.py              # Reel upload, following
│   ├── urls.py
│   └── admin.py
├── payments/                  # Paystack integration
│   ├── models.py             # Transaction, Commission
│   ├── views.py              # Payment processing
│   ├── urls.py
│   └── paystack.py           # Paystack API wrapper
├── core/                      # Base templates & dashboard
│   ├── views.py              # Dashboard routing
│   ├── urls.py
│   └── context_processors.py
├── templates/                 # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   ├── events/
│   ├── artists/
│   ├── payments/
│   └── core/
├── static/                    # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
└── media/                     # User uploads
    ├── avatars/
    ├── reels/
    └── event_images/
```

## 🔧 Tech Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Frontend**: Bootstrap 5
- **JavaScript**: jQuery + AJAX
- **Payments**: Paystack
- **Deployment**: Render.com
- **File Storage**: Local (upgradeable to S3)

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/Br41n7/Tick
cd Tick

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your keys

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create directories
mkdir -p static staticfiles media/avatars media/reels media/event_images

# Run server
python manage.py runserver
```

## 🔑 Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
ADMIN_COMMISSION_RATE=0.10
```

## 💳 Paystack Integration

### Setup
1. Create Paystack account at https://paystack.com
2. Get API keys from dashboard
3. Add keys to .env file
4. Configure webhook URL: `https://yourdomain.com/payments/webhook/`

### Commission System
- 10% admin commission on all bookings
- Automatic calculation and tracking
- Host receives 90% of ticket price
- Commission tracked in Transaction model

## 🎨 Key Features Detail

### Event Booking Flow
1. User browses events
2. Clicks "Book Ticket"
3. Redirected to Paystack checkout
4. Payment processed
5. Booking confirmed
6. Email notification sent
7. Commission calculated and recorded

### Role Upgrade Flow
1. User requests upgrade (Artist/Host)
2. Provides reason
3. Admin reviews request
4. Approves/rejects
5. User role updated
6. Access granted to new features

### Social Sharing
- WhatsApp share with pre-filled message
- Facebook share with event details
- Twitter share with hashtags
- Share count tracked per event
- Analytics available to hosts

## 📊 Database Models

### Accounts App
- **CustomUser**: Extended user with roles
- **RoleUpgradeRequest**: Track upgrade requests

### Events App
- **Event**: Event details, pricing, venue
- **Booking**: Ticket bookings with payment
- **EventFavorite**: User favorites
- **EventShare**: Share tracking

### Artists App
- **ArtistProfile**: Artist details and stats
- **Reel**: Video/image uploads
- **ReelView**: View tracking
- **ReelLike**: Like tracking
- **Follow**: Follow relationships

### Payments App
- **Transaction**: Payment records
- **Commission**: Admin commission tracking
- **Payout**: Host payout records

## 🎯 User Dashboards

### Ordinary User Dashboard
- Upcoming bookings
- Favorite events
- Favorite reels
- Followed artists
- Booking history

### Artist Dashboard
- Upload reels
- View stats (followers, plays, likes)
- Manage profile
- View earnings (if also host)

### Host Dashboard
- Create/manage events
- View bookings
- Earnings report
- Event analytics

### Admin Dashboard
- User management
- Event approval
- Transaction monitoring
- Platform analytics
- Role upgrade requests

## 🚀 Deployment

### Render.com Deployment
1. Push code to GitHub
2. Create Render account
3. Create PostgreSQL database
4. Create web service
5. Configure environment variables
6. Deploy!

See `DEPLOYMENT.md` for detailed instructions.

## 📱 Responsive Design

- Mobile-first approach
- Bootstrap 5 responsive grid
- Touch-friendly interfaces
- Optimized for all screen sizes

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- HTTPS enforcement (production)
- Secure file uploads
- Payment security via Paystack

## 📈 Analytics

### Event Analytics
- Total views
- Favorites count
- Share count
- Booking count
- Revenue generated

### Artist Analytics
- Total followers
- Reel views
- Reel likes
- Engagement rate

### Platform Analytics (Admin)
- Total users by role
- Total events
- Total bookings
- Total revenue
- Commission earned

## 🎉 Next Steps

1. Run the application locally
2. Create test users with different roles
3. Test all features
4. Configure Paystack
5. Deploy to production

## 📚 Documentation

- README.md - Main documentation
- ENTERTAINMENT_DEPLOYMENT.md - Deployment guide
- API_DOCS.md - API reference
- USER_GUIDE.md - User manual

## 🆘 Support

For issues or questions:
- GitHub Issues
- Email: iyanuolalegan1@gmail.com
- Documentation: See README.md

## 📝 License

MIT License

---

**Status**: ✅ Complete and ready for deployment!