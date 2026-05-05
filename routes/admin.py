from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.utils import secure_filename
from database.db import get_db
from datetime import datetime
import os
import uuid

admin_bp = Blueprint('admin', __name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def admin_required():
    return session.get('role') == 'admin'


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_time_ago(timestamp):
    if not timestamp:
        return "N/A"

    try:
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.split('.')[0])
        else:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

        diff = datetime.now() - dt

        if diff.days == 0:
            if diff.seconds < 60:
                return "Just now"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60} mins ago"
            else:
                return f"{diff.seconds // 3600} hrs ago"
        elif diff.days == 1:
            return "Yesterday"
        else:
            return dt.strftime("%d %b %Y")

    except Exception:
        return timestamp


@admin_bp.route('/admin')
def admin_dashboard():
    if not admin_required():
        return redirect(url_for('property.index'))

    conn = get_db()
    properties_count = conn.execute('SELECT COUNT(*) FROM properties').fetchone()[0]
    for_sale_count = conn.execute("SELECT COUNT(*) FROM properties WHERE status = 'For Sale'").fetchone()[0]
    for_rent_count = conn.execute("SELECT COUNT(*) FROM properties WHERE status = 'For Rent'").fetchone()[0]
    users_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    enquiries_count = conn.execute('SELECT COUNT(*) FROM enquiries').fetchone()[0]
    recent_properties = conn.execute('SELECT * FROM properties ORDER BY created_at DESC LIMIT 5').fetchall()
    
    # Fetch enquiries safely without complex joins
    enquiries = conn.execute('SELECT * FROM enquiries ORDER BY created_at DESC LIMIT 5').fetchall()
    
    # Ensure enquiries is always a list
    if enquiries is None:
        enquiries = []
    
    conn.close()

    return render_template(
        'admin_dashboard.html',
        properties_count=properties_count,
        for_sale_count=for_sale_count,
        for_rent_count=for_rent_count,
        users_count=users_count,
        enquiries_count=enquiries_count,
        recent_properties=recent_properties,
        enquiries=enquiries,
        format_time_ago=format_time_ago
    )


@admin_bp.route('/admin/properties')
def admin_properties():
    if not admin_required():
        return redirect(url_for('property.index'))

    conn = get_db()
    properties = conn.execute('SELECT * FROM properties ORDER BY created_at DESC').fetchall()
    conn.close()

    return render_template('admin_properties.html', properties=properties)


@admin_bp.route('/admin/properties/add', methods=['GET', 'POST'])
def add_property():
    if not admin_required():
        return redirect(url_for('property.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        location = request.form.get('location', '').strip()
        bedrooms = request.form.get('bedrooms', '').strip()
        bathrooms = request.form.get('bathrooms', '').strip()
        area_sqft = request.form.get('area_sqft', '').strip()
        property_type = request.form.get('property_type', '').strip()
        status = request.form.get('status', '').strip()
        image = request.files.get('image')

        if not (title and description and price and location and bedrooms and bathrooms and area_sqft and property_type and status and image and image.filename):
            flash('All property fields are required, including an image.', 'error')
            return render_template('add_property.html')

        if not is_allowed_file(image.filename):
            flash('Only JPG, JPEG, PNG, and WEBP image formats are allowed.', 'error')
            return render_template('add_property.html')

        extension = os.path.splitext(image.filename)[1].lower()
        image_filename = f"{uuid.uuid4()}{extension}"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image.save(os.path.join(UPLOAD_FOLDER, image_filename))

        conn = get_db()
        conn.execute(
            'INSERT INTO properties (title, description, price, location, bedrooms, bathrooms, area_sqft, property_type, status, image_filename, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (title, description, float(price), location, int(bedrooms), int(bathrooms), int(area_sqft), property_type, status, image_filename, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        flash('Property created successfully.', 'success')
        return redirect(url_for('admin.admin_properties'))

    return render_template('add_property.html')


@admin_bp.route('/admin/properties/<int:property_id>/edit', methods=['GET', 'POST'])
def edit_property(property_id):
    if not admin_required():
        return redirect(url_for('property.index'))

    conn = get_db()
    property_item = conn.execute('SELECT * FROM properties WHERE id = ?', (property_id,)).fetchone()

    if not property_item:
        conn.close()
        flash('Property not found.', 'error')
        return redirect(url_for('admin.admin_properties'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        location = request.form.get('location', '').strip()
        bedrooms = request.form.get('bedrooms', '').strip()
        bathrooms = request.form.get('bathrooms', '').strip()
        area_sqft = request.form.get('area_sqft', '').strip()
        property_type = request.form.get('property_type', '').strip()
        status = request.form.get('status', '').strip()
        image = request.files.get('image')

        if not (title and description and price and location and bedrooms and bathrooms and area_sqft and property_type and status):
            flash('Please fill out all fields before saving changes.', 'error')
            conn.close()
            return render_template('edit_property.html', property=property_item)

        new_filename = property_item['image_filename']
        if image and image.filename:
            if not is_allowed_file(image.filename):
                flash('Only JPG, JPEG, PNG, and WEBP image formats are allowed.', 'error')
                conn.close()
                return render_template('edit_property.html', property=property_item)

            extension = os.path.splitext(image.filename)[1].lower()
            new_filename = f"{uuid.uuid4()}{extension}"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(os.path.join(UPLOAD_FOLDER, new_filename))
            old_path = os.path.join(UPLOAD_FOLDER, property_item['image_filename']) if property_item['image_filename'] else None
            if old_path and os.path.exists(old_path):
                os.remove(old_path)

        conn.execute(
            'UPDATE properties SET title = ?, description = ?, price = ?, location = ?, bedrooms = ?, bathrooms = ?, area_sqft = ?, property_type = ?, status = ?, image_filename = ? WHERE id = ?',
            (title, description, float(price), location, int(bedrooms), int(bathrooms), int(area_sqft), property_type, status, new_filename, property_id)
        )
        conn.commit()
        conn.close()

        flash('Property updated successfully.', 'success')
        return redirect(url_for('admin.admin_properties'))

    conn.close()
    return render_template('edit_property.html', property=property_item)


@admin_bp.route('/admin/properties/<int:property_id>/delete', methods=['POST'])
def delete_property(property_id):
    if not admin_required():
        return redirect(url_for('property.index'))

    conn = get_db()
    property_item = conn.execute('SELECT image_filename FROM properties WHERE id = ?', (property_id,)).fetchone()

    if property_item and property_item['image_filename']:
        image_path = os.path.join(UPLOAD_FOLDER, property_item['image_filename'])
        if os.path.exists(image_path):
            os.remove(image_path)

    conn.execute('DELETE FROM properties WHERE id = ?', (property_id,))
    conn.commit()
    conn.close()

    flash('Property removed permanently.', 'success')
    return redirect(url_for('admin.admin_properties'))


@admin_bp.route('/view_enquiries')
def view_enquiries():
    if not admin_required():
        return redirect(url_for('property.index'))

    conn = get_db()
    enquiries = conn.execute(
        'SELECT e.*, p.title AS property_title, u.username AS user_name '
        'FROM enquiries e '
        'LEFT JOIN properties p ON e.property_id = p.id '
        'LEFT JOIN users u ON e.user_id = u.id '
        'ORDER BY e.created_at DESC'
    ).fetchall()
    conn.close()

    return render_template('enquiries.html', enquiries=enquiries)
