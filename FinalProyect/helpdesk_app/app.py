from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


# DATABASE CONNECTION


def get_db_connection():
    """Create and return a database connection."""
    return pymysql.connect(
        host=app.config["DB_HOST"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor
    )


# DECORATORS FOR AUTHENTICATION AND AUTHORIZATION


def login_required(f):
    """Decorator to ensure user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to ensure user has the required role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_role" not in session or session["user_role"] not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# MAIN ROUTES


@app.route("/")
def index():
    """Redirect to dashboard if logged in, otherwise to login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard with ticket statistics."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Get ticket counts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM tickets 
            GROUP BY status
        """)
        status_stats = cursor.fetchall()
        
        # Get ticket counts by priority
        cursor.execute("""
            SELECT priority, COUNT(*) as count 
            FROM tickets 
            GROUP BY priority
        """)
        priority_stats = cursor.fetchall()
        
        # Get total tickets
        cursor.execute("SELECT COUNT(*) as total FROM tickets")
        total_tickets = cursor.fetchone()["total"]
        
        # Get total users
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()["total"]
        
        # Get recent tickets (last 5)
        user_role = session.get("user_role")
        user_id = session.get("user_id")
        
        if user_role == "ADMIN":
            cursor.execute("""
                SELECT t.*, u.name AS created_by_name 
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                ORDER BY t.created_at DESC
                LIMIT 5
            """)
        elif user_role == "AGENT":
            cursor.execute("""
                SELECT t.*, u.name AS created_by_name 
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                WHERE t.assigned_to = %s OR t.assigned_to IS NULL
                ORDER BY t.created_at DESC
                LIMIT 5
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT t.*, u.name AS created_by_name 
                FROM tickets t
                JOIN users u ON t.created_by = u.id
                WHERE t.created_by = %s
                ORDER BY t.created_at DESC
                LIMIT 5
            """, (user_id,))
        
        recent_tickets = cursor.fetchall()
    conn.close()
    
    return render_template("dashboard.html", 
                         status_stats=status_stats,
                         priority_stats=priority_stats,
                         total_tickets=total_tickets,
                         total_users=total_users,
                         recent_tickets=recent_tickets)


# AUTHENTICATION ROUTES


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user["password_hash"], password):
            # Store user info in session
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash("Welcome, {}!".format(user["name"]), "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("register"))
        
        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return redirect(url_for("register"))
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already registered.", "danger")
                conn.close()
                return redirect(url_for("register"))
            
            # Create new user
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, 'USER')
            """, (name, email, password_hash))
            conn.commit()
        conn.close()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")


# TICKET ROUTES


@app.route("/tickets")
@login_required
def tickets_list():
    """Display list of tickets based on user role."""
    user_id = session["user_id"]
    user_role = session["user_role"]
    
    # Get filter parameters
    status_filter = request.args.get("status", "")
    priority_filter = request.args.get("priority", "")
    search_query = request.args.get("search", "")
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Base query
        base_query = """
            SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
            FROM tickets t
            JOIN users u ON t.created_by = u.id
            LEFT JOIN users a ON t.assigned_to = a.id
            WHERE 1=1
        """
        params = []
        
        # Role-based filtering
        if user_role == "ADMIN":
            pass  # Admin sees all tickets
        elif user_role == "AGENT":
            base_query += " AND (t.assigned_to = %s OR t.assigned_to IS NULL)"
            params.append(user_id)
        else:  # USER
            base_query += " AND t.created_by = %s"
            params.append(user_id)
        
        # Apply filters
        if status_filter:
            base_query += " AND t.status = %s"
            params.append(status_filter)
        
        if priority_filter:
            base_query += " AND t.priority = %s"
            params.append(priority_filter)
        
        if search_query:
            base_query += " AND (t.title LIKE %s OR t.description LIKE %s)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        
        base_query += " ORDER BY t.created_at DESC"
        
        cursor.execute(base_query, params)
        tickets = cursor.fetchall()
    conn.close()
    
    return render_template("tickets_list.html", 
                         tickets=tickets,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         search_query=search_query)

@app.route("/tickets/new", methods=["GET", "POST"])
@login_required
def ticket_new():
    """Create a new ticket."""
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")
        created_by = session["user_id"]
        
        if not title or not description:
            flash("Title and description are required.", "warning")
            return redirect(url_for("ticket_new"))
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO tickets (title, description, priority, created_by)
                VALUES (%s, %s, %s, %s)
            """, (title, description, priority, created_by))
            conn.commit()
        conn.close()
        
        flash("Ticket created successfully.", "success")
        return redirect(url_for("tickets_list"))
    
    return render_template("ticket_new.html")

@app.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    """Display ticket details and comments."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Get ticket details
        cursor.execute("""
            SELECT t.*, u.name AS created_by_name, a.name AS assigned_to_name
            FROM tickets t
            JOIN users u ON t.created_by = u.id
            LEFT JOIN users a ON t.assigned_to = a.id
            WHERE t.id = %s
        """, (ticket_id,))
        ticket = cursor.fetchone()
        
        if not ticket:
            flash("Ticket not found.", "danger")
            conn.close()
            return redirect(url_for("tickets_list"))
        
        # Check access permissions
        user_role = session["user_role"]
        user_id = session["user_id"]
        
        if user_role == "USER" and ticket["created_by"] != user_id:
            flash("You do not have permission to view this ticket.", "danger")
            conn.close()
            return redirect(url_for("tickets_list"))
        
        # Get comments
        cursor.execute("""
            SELECT c.*, u.name AS user_name
            FROM ticket_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.ticket_id = %s
            ORDER BY c.created_at ASC
        """, (ticket_id,))
        comments = cursor.fetchall()
        
        # Get agents for assignment dropdown
        cursor.execute("SELECT id, name FROM users WHERE role IN ('ADMIN', 'AGENT')")
        agents = cursor.fetchall()
    conn.close()
    
    return render_template("ticket_detail.html",
                         ticket=ticket,
                         comments=comments,
                         agents=agents)

@app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
@login_required
@role_required("ADMIN", "AGENT")
def ticket_update(ticket_id):
    """Update ticket status and assignment."""
    status = request.form.get("status")
    priority = request.form.get("priority")
    assigned_to = request.form.get("assigned_to") or None
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE tickets
            SET status = %s, priority = %s, assigned_to = %s
            WHERE id = %s
        """, (status, priority, assigned_to, ticket_id))
        conn.commit()
    conn.close()
    
    flash("Ticket updated.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

@app.route("/tickets/<int:ticket_id>/update-ajax", methods=["POST"])
@login_required
@role_required("ADMIN", "AGENT")
def ticket_update_ajax(ticket_id):
    """Update ticket via AJAX (jQuery)."""
    data = request.get_json()
    status = data.get("status")
    priority = data.get("priority")
    assigned_to = data.get("assigned_to") or None
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE tickets
            SET status = %s, priority = %s, assigned_to = %s
            WHERE id = %s
        """, (status, priority, assigned_to, ticket_id))
        conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Ticket updated successfully"})

@app.route("/tickets/<int:ticket_id>/comments", methods=["POST"])
@login_required
def comment_add(ticket_id):
    """Add a comment to a ticket."""
    comment_text = request.form.get("comment")
    user_id = session["user_id"]
    
    if not comment_text:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO ticket_comments (ticket_id, user_id, comment)
            VALUES (%s, %s, %s)
        """, (ticket_id, user_id, comment_text))
        conn.commit()
    conn.close()
    
    flash("Comment added.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

@app.route("/tickets/<int:ticket_id>/comments-ajax", methods=["POST"])
@login_required
def comment_add_ajax(ticket_id):
    """Add comment via AJAX (jQuery)."""
    data = request.get_json()
    comment_text = data.get("comment")
    user_id = session["user_id"]
    user_name = session["user_name"]
    
    if not comment_text:
        return jsonify({"success": False, "message": "Comment cannot be empty"})
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO ticket_comments (ticket_id, user_id, comment)
            VALUES (%s, %s, %s)
        """, (ticket_id, user_id, comment_text))
        conn.commit()
        
        # Get the newly created comment
        cursor.execute("""
            SELECT c.*, u.name AS user_name
            FROM ticket_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = LAST_INSERT_ID()
        """)
        new_comment = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "success": True, 
        "message": "Comment added",
        "comment": {
            "id": new_comment["id"],
            "user_name": new_comment["user_name"],
            "comment": new_comment["comment"],
            "created_at": new_comment["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        }
    })


# USER MANAGEMENT ROUTES (ADMIN ONLY)


@app.route("/users")
@login_required
@role_required("ADMIN")
def users_list():
    """Display list of all users (Admin only)."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, email, role, created_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
    conn.close()
    
    return render_template("users_list.html", users=users)

@app.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@role_required("ADMIN")
def user_change_role(user_id):
    """Change a user's role (Admin only)."""
    new_role = request.form.get("role")
    
    if new_role not in ["ADMIN", "AGENT", "USER"]:
        flash("Invalid role.", "danger")
        return redirect(url_for("users_list"))
    
    # Prevent admin from changing their own role
    if user_id == session["user_id"]:
        flash("You cannot change your own role.", "warning")
        return redirect(url_for("users_list"))
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        conn.commit()
    conn.close()
    
    flash("Role updated.", "success")
    return redirect(url_for("users_list"))

@app.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN")
def user_delete(user_id):
    """Delete a user (Admin only)."""
    # Prevent admin from deleting themselves
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("users_list"))
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Check if user has tickets
        cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE created_by = %s", (user_id,))
        ticket_count = cursor.fetchone()["count"]
        
        if ticket_count > 0:
            flash("Cannot delete user with existing tickets.", "danger")
            conn.close()
            return redirect(url_for("users_list"))
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
    conn.close()
    
    flash("User deleted.", "success")
    return redirect(url_for("users_list"))


# API ENDPOINTS FOR STATISTICS (DASHBOARD)


@app.route("/api/stats")
@login_required
def api_stats():
    """Get ticket statistics for dashboard charts."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM tickets 
            GROUP BY status
        """)
        status_stats = cursor.fetchall()
        
        cursor.execute("""
            SELECT priority, COUNT(*) as count 
            FROM tickets 
            GROUP BY priority
        """)
        priority_stats = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "status": status_stats,
        "priority": priority_stats
    })


# ERROR HANDLERS


@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error_code=500, error_message="Internal server error"), 500


# MAIN ENTRY POINT


if __name__ == "__main__":
    app.run(debug=True)
