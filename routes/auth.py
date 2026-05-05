from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
from datetime import datetime

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user'):
        return redirect(url_for('property.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash('Please complete all fields to register.', 'error')
            return render_template('register.html')

        conn = get_db()
        existing = conn.execute(
            'SELECT id FROM users WHERE email = ? OR username = ?',
            (email, username)
        ).fetchone()

        if existing:
            flash('Email or username already exists. Please choose another.', 'error')
            conn.close()
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, 0, ?)',
            (username, email, password_hash, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('property.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter your email and password.', 'error')
            return render_template('login.html')

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user['email']
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'admin' if user['is_admin'] else 'user'
            flash(f'Welcome back, {user["username"]}.', 'success')
            return redirect(url_for('property.index'))

        flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
