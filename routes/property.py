from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from database.db import get_db
from urllib.parse import urlencode
from datetime import datetime

def send_email(subject, body):
    try:
        import smtplib
        from email.mime.text import MIMEText
        import os

        sender = os.environ.get("EMAIL_USER")
        password = os.environ.get("EMAIL_PASS")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = sender

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("Email error:", e)

property_bp = Blueprint('property', __name__)


def ensure_default_properties(conn, minimum=12):
    total = conn.execute('SELECT COUNT(*) FROM properties').fetchone()[0]
    if total >= minimum:
        return

    # Delete existing properties to refresh with updated data
    conn.execute("DELETE FROM properties")

    default_properties = [
        {
            'title': 'Parkview Penthouse',
            'description': 'A premium 3 bedroom penthouse with city skyline views and premium amenities.',
            'price': 12500000,
            'location': 'Indiranagar, Bangalore',
            'bedrooms': 3,
            'bathrooms': 3,
            'area_sqft': 1850,
            'property_type': 'Apartment',
            'status': 'For Sale',
            'image_filename': 'house1.jpg'
        },
        {
            'title': 'Lakefront Villa',
            'description': 'Elegant villa with private garden, pool, and easy access to local parks.',
            'price': 23500000,
            'location': 'Mysuru',
            'bedrooms': 5,
            'bathrooms': 4,
            'area_sqft': 4200,
            'property_type': 'Villa',
            'status': 'For Sale',
            'image_filename': 'house2.jpg'
        },
        {
            'title': 'City Center Studio',
            'description': 'Stylish studio apartment located near transit, shops, and dining.',
            'price': 6200000,
            'location': 'Electronic City, Bangalore',
            'bedrooms': 1,
            'bathrooms': 1,
            'area_sqft': 650,
            'property_type': 'Apartment',
            'status': 'For Rent',
            'image_filename': 'house3.jpg'
        },
        {
            'title': 'Hilltop Residence',
            'description': 'Luxury family home with panoramic views and spacious outdoor living areas.',
            'price': 18900000,
            'location': 'Chennai (Anna Nagar)',
            'bedrooms': 4,
            'bathrooms': 4,
            'area_sqft': 3600,
            'property_type': 'Villa',
            'status': 'For Sale',
            'image_filename': 'house4.jpg'
        },
        {
            'title': 'Modern Office Space',
            'description': 'Contemporary commercial space suited for startups and creative businesses.',
            'price': 9800000,
            'location': 'Chennai (T Nagar)',
            'bedrooms': 2,
            'bathrooms': 2,
            'area_sqft': 2500,
            'property_type': 'Commercial',
            'status': 'For Rent',
            'image_filename': 'house5.jpg'
        },
        {
            'title': 'Garden Townhouse',
            'description': 'Cozy townhouse with curated landscaping and smart home finishes.',
            'price': 11250000,
            'location': 'Whitefield, Bangalore',
            'bedrooms': 3,
            'bathrooms': 3,
            'area_sqft': 2100,
            'property_type': 'Apartment',
            'status': 'For Sale',
            'image_filename': 'house6.jpg'
        },
        {
            'title': 'Premium Beach Plot',
            'description': 'Generous plot ideal for a custom home with local amenities nearby.',
            'price': 14200000,
            'location': 'Chennai (T Nagar)',
            'bedrooms': 3,
            'bathrooms': 2,
            'area_sqft': 7200,
            'property_type': 'Plot',
            'status': 'For Sale',
            'image_filename': 'house7.jpg'
        },
        {
            'title': 'Luxury Rental Villa',
            'description': 'Fully furnished rental villa with high-end finishes and private outside space.',
            'price': 1850000,
            'location': 'Mysuru',
            'bedrooms': 4,
            'bathrooms': 4,
            'area_sqft': 3800,
            'property_type': 'Villa',
            'status': 'For Rent',
            'image_filename': 'house8.jpg'
        },
        {
            'title': 'Urban Loft',
            'description': 'Open-plan loft designed for modern living and productive daily routines.',
            'price': 8600000,
            'location': 'Koramangala, Bangalore',
            'bedrooms': 2,
            'bathrooms': 2,
            'area_sqft': 1320,
            'property_type': 'Apartment',
            'status': 'For Sale',
            'image_filename': 'house9.jpg'
        },
        {
            'title': 'Corner Commercial Plot',
            'description': 'Prime corner plot suited for retail or office development.',
            'price': 10200000,
            'location': 'Indiranagar, Bangalore',
            'bedrooms': 2,
            'bathrooms': 2,
            'area_sqft': 5400,
            'property_type': 'Plot',
            'status': 'For Sale',
            'image_filename': 'house10.jpg'
        },
        {
            'title': 'Highrise Executive Suite',
            'description': 'Executive apartment with premium amenities and concierge services.',
            'price': 14800000,
            'location': 'Electronic City, Bangalore',
            'bedrooms': 3,
            'bathrooms': 3,
            'area_sqft': 1750,
            'property_type': 'Apartment',
            'status': 'For Rent',
            'image_filename': 'house11.jpg'
        },
        {
            'title': 'Boutique Retail Space',
            'description': 'High-visibility retail showroom in a busy shopping neighborhood.',
            'price': 8900000,
            'location': 'Chennai (Anna Nagar)',
            'bedrooms': 2,
            'bathrooms': 1,
            'area_sqft': 1500,
            'property_type': 'Commercial',
            'status': 'For Sale',
            'image_filename': 'house12.jpg'
        }
    ]

    for property_data in default_properties[:max(0, minimum - total)]:
        conn.execute(
            'INSERT INTO properties (title, description, price, location, bedrooms, bathrooms, area_sqft, property_type, status, image_filename, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                property_data['title'],
                property_data['description'],
                property_data['price'],
                property_data['location'],
                property_data['bedrooms'],
                property_data['bathrooms'],
                property_data['area_sqft'],
                property_data['property_type'],
                property_data['status'],
                property_data['image_filename'],
                datetime.now().isoformat()
            )
        )
    conn.commit()


@property_bp.route('/', methods=['GET'])
def index():
    conn = get_db()
    ensure_default_properties(conn)
    show_all = 'user_id' in session
    query = 'SELECT * FROM properties ORDER BY id DESC'
    if not show_all:
        query += ' LIMIT 3'
    featured = conn.execute(query).fetchall()
    conn.close()

    return render_template('index.html', featured=featured, show_all=show_all)


@property_bp.route('/properties')
def properties():

    args = request.args
    search = args.get('search', '').strip()
    property_type = args.get('property_type', '').strip() or args.get('type', '').strip()
    status = args.get('status', '').strip()
    min_price = args.get('min_price', '').strip()
    max_price = args.get('max_price', '').strip()
    bedrooms = args.get('bedrooms', '').strip()

    filters = []
    params = []

    if search:
        filters.append('(LOWER(title) LIKE ? OR LOWER(location) LIKE ?)')
        params.extend([f'%{search.lower()}%'] * 2)

    if property_type and property_type != 'Any':
        filters.append('property_type = ?')
        params.append(property_type)

    if status and status != 'Any':
        filters.append('status = ?')
        params.append(status)

    if min_price:
        try:
            filters.append('price >= ?')
            params.append(float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            filters.append('price <= ?')
            params.append(float(max_price))
        except ValueError:
            pass

    if bedrooms:
        try:
            filters.append('bedrooms >= ?')
            params.append(int(bedrooms))
        except ValueError:
            pass

    where_clause = f" WHERE {' AND '.join(filters)}" if filters else ''

    # Show all properties on the listings page, ordered newest first.
    page = 1

    conn = get_db()
    ensure_default_properties(conn)
    total = conn.execute(f'SELECT COUNT(*) FROM properties{where_clause}', params).fetchone()[0]
    properties = conn.execute(
        f'SELECT * FROM properties{where_clause} ORDER BY id DESC',
        params
    ).fetchall()
    conn.close()

    page_count = 1
    has_prev = False
    has_next = False

    preserved_args = {
        key: value
        for key, value in args.items()
        if key != 'page' and value
    }
    query_string = urlencode(preserved_args)

    filter_values = {
        'search': search,
        'property_type': property_type,
        'status': status,
        'min_price': min_price,
        'max_price': max_price,
        'bedrooms': bedrooms,
    }

    return render_template(
        'properties.html',
        properties=properties,
        page=page,
        page_count=page_count,
        has_prev=has_prev,
        has_next=has_next,
        query_string=query_string,
        total=total,
        filters=filter_values
    )


@property_bp.route('/property/<int:property_id>', methods=['GET', 'POST'])
def property_detail(property_id):
    conn = get_db()
    property_item = conn.execute(
        'SELECT * FROM properties WHERE id = ?',
        (property_id,)
    ).fetchone()

    if not property_item:
        conn.close()
        flash('Property not found.', 'error')
        return redirect(url_for('property.properties'))

    if request.method == 'POST':
        name = request.form.get('name', session.get('username', '')).strip()
        email = request.form.get('email', session.get('user', '')).strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please complete the enquiry form before sending.', 'error')
            conn.close()
            return redirect(url_for('property.property_detail', property_id=property_id))

        user = conn.execute(
            'SELECT id FROM users WHERE email = ?',
            (session.get('user'),)
        ).fetchone()

        user_id = user['id'] if user else None
        conn.execute(
            'INSERT INTO enquiries (user_id, property_id, name, email, message, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, property_id, name, email, message, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        # Send email
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}\nProperty: {property_item['title']}"
        send_email(f"Enquiry for {property_item['title']}", body)

        flash('Your enquiry has been submitted successfully.', 'success')
        return redirect(url_for('property.property_detail', property_id=property_id))

    similar = conn.execute(
        'SELECT * FROM properties WHERE location = ? AND id != ? ORDER BY created_at DESC LIMIT 3',
        (property_item['location'], property_id)
    ).fetchall()
    conn.close()

    return render_template(
        'property_detail.html',
        property=property_item,
        similar=similar
    )


@property_bp.route('/favorites/add/<int:property_id>')
def add_favorite(property_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    user = conn.execute('SELECT id FROM users WHERE email = ?', (session['user'],)).fetchone()
    if user:
        existing = conn.execute(
            'SELECT id FROM favorites WHERE user_id = ? AND property_id = ?',
            (user['id'], property_id)
        ).fetchone()
        if not existing:
            conn.execute(
                'INSERT INTO favorites (user_id, property_id) VALUES (?, ?)',
                (user['id'], property_id)
            )
            conn.commit()
            flash('Added to your favorites.', 'success')
        else:
            flash('This property is already in your favorites.', 'info')
    conn.close()

    return redirect(url_for('property.favorites'))


@property_bp.route('/favorites/remove/<int:property_id>', methods=['POST'])
def remove_favorite(property_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    user = conn.execute('SELECT id FROM users WHERE email = ?', (session['user'],)).fetchone()
    if user:
        conn.execute(
            'DELETE FROM favorites WHERE user_id = ? AND property_id = ?',
            (user['id'], property_id)
        )
        conn.commit()
        flash('Removed from favorites.', 'info')
    conn.close()

    return redirect(url_for('property.favorites'))


@property_bp.route('/favorites')
def favorites():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db()
    favorite_properties = conn.execute(
        'SELECT p.* FROM properties p '
        'JOIN favorites f ON p.id = f.property_id '
        'JOIN users u ON f.user_id = u.id '
        'WHERE u.email = ? '
        'ORDER BY f.id DESC',
        (session['user'],)
    ).fetchall()
    conn.close()

    return render_template('favorites.html', properties=favorite_properties)


@property_bp.route('/contact/<int:property_id>')
def contact_property(property_id):
    return redirect(url_for('property.property_detail', property_id=property_id))


@property_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not (name and email and subject and message):
            flash('Please complete the contact form before sending.', 'error')
            return render_template('contact.html')

        # Save to database with SQLite current timestamp
        conn = get_db()
        conn.execute(
            "INSERT INTO enquiries (name, email, message, created_at) VALUES (?, ?, ?, datetime('now'))",
            (name, email, message)
        )
        conn.commit()
        conn.close()

        # Send email
        body = f"""
New Enquiry:

Name: {name}
Email: {email}
Message: {message}
"""
        send_email("New Enquiry", body)

        flash('Your message has been sent successfully. We will be in touch soon.', 'success')
        return redirect(url_for('property.success'))

    return render_template('contact.html')


@property_bp.route('/about')
def about():
    return render_template('about.html')


@property_bp.route('/success')
def success():
    return render_template('success.html')
