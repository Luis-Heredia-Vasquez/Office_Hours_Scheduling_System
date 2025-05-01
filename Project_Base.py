from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from functools import wraps
app = Flask(__name__, template_folder='frontend')
app.secret_key = 'GroupProject'

DB = 'appointments.db'

# Database initialization
def init_db():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'professor')),
                email TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()

# Appointment Data Structures
# Appointment Node
class AppointmentNode:
    def __init__(self, student_name, time_slot):
        self.student_name = student_name
        self.time_slot = time_slot
        self.next = None

# Queue for Waitlist
class Queue:
    def __init__(self):
        self.head = None
        self.tail = None

    def enqueue(self, student_name):
        new_node = AppointmentNode(student_name, None)
        if self.tail:
            self.tail.next = new_node
        self.tail = new_node
        if not self.head:
            self.head = new_node

    def dequeue(self):
        if not self.head:
            return None
        student_name = self.head.student_name
        self.head = self.head.next
        if not self.head:
            self.tail = None
        return student_name

    def is_empty(self):
        return self.head is None

# AppointmentList with O(1) cancel support
class AppointmentList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.booked_slots = {}  # time_slot.lower() -> AppointmentNode
        self.student_slot_map = {}  # (student.lower(), time.lower()) -> AppointmentNode
        self.prev_node_map = {}  # (student.lower(), time.lower()) -> previous node
        self.waitlist = {}  # time_slot.lower() -> Queue
        self.canceled_stack = []  # stack of (student_name, time_slot)

    def book(self, student_name, time_slot, schedule):
        slot_key = time_slot.lower()
        student_key = student_name.lower()
        key = (student_key, slot_key)

        if slot_key not in schedule['valid_slots']:
            return "Invalid time slot"

        if slot_key in self.booked_slots:
            # Add to waitlist using Queue
            if slot_key not in self.waitlist:
                self.waitlist[slot_key] = Queue()
            self.waitlist[slot_key].enqueue(student_name)
            return "Time slot already booked. You have been Waitlisted"

        # Book the appointment
        new_node = AppointmentNode(student_name, time_slot)
        new_node.next = self.head
        if self.head:
            self.prev_node_map[(self.head.student_name.lower(), self.head.time_slot.lower())] = new_node
        self.head = new_node
        if self.tail is None:
            self.tail = new_node

        self.booked_slots[slot_key] = new_node
        self.student_slot_map[key] = new_node
        self.prev_node_map[key] = None

        return "Booked"

    def cancel(self, student_name, time_slot, schedule):
        slot_key = time_slot.lower()
        student_key = student_name.lower()
        key = (student_key, slot_key)

        if key not in self.student_slot_map:
            return "No appointment found"

        node_to_remove = self.student_slot_map[key]
        prev_node = self.prev_node_map.get(key)

        # Remove node from list
        if prev_node:
            prev_node.next = node_to_remove.next
        else:
            self.head = node_to_remove.next

        # Update tail if needed
        if node_to_remove == self.tail:
            self.tail = prev_node

        # Update prev_node_map for node after removed node
        next_node = node_to_remove.next
        if next_node:
            self.prev_node_map[(next_node.student_name.lower(), next_node.time_slot.lower())] = prev_node

        # Clean up maps
        del self.student_slot_map[key]
        del self.booked_slots[slot_key]
        del self.prev_node_map[key]

        self.canceled_stack.append((student_name, time_slot))

        # Promote from waitlist
        if slot_key in self.waitlist and not self.waitlist[slot_key].is_empty():
            next_student = self.waitlist[slot_key].dequeue()
            self.book(next_student, time_slot, schedule)
            return f"Your appointment was canceled. {next_student} from the waitlist has been booked for {time_slot}."

        return "Canceled"

    def undo_cancel(self, student_name, schedule):
        if not self.canceled_stack:
            return "No canceled appointments to undo."

        last_student, last_time = self.canceled_stack[-1]
        if last_student.lower() != student_name.lower():
            return "You can only undo your own cancellations."

        self.canceled_stack.pop()
        result = self.book(student_name, last_time, schedule)
        return f"Undo successful: {result} for {student_name} at {last_time}"

# Professors
professors = {
    "Dr. Smith": {
        'appointments': AppointmentList(),
        'schedule': [
            "Monday 2PM", "Monday 3PM", "Monday 4PM",
            "Wednesday 3PM", "Wednesday 4PM", "Wednesday 5PM"
        ],
        'email': 'dr.smith@example.com'
    },
    "Dr. Lee": {
        'appointments': AppointmentList(),
        'schedule': [
            "Tuesday 1PM", "Tuesday 2PM", "Tuesday 3PM",
            "Thursday 10AM", "Thursday 11AM", "Thursday 12PM"
        ],
        'email': 'dr.lee@example.com'
    }
}

# Add valid_slots lookup table
for prof in professors.values():
    prof['valid_slots'] = {s.lower(): True for s in prof['schedule']}
    
# Login required 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        email = request.form['email']

        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                               (username, password, role, email))
                conn.commit()
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username or email already exists.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = username
                session['role'] = user[1]
                flash('Login successful.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    user_appointments = []
    for professor, details in professors.items():
        current = details['appointments'].head
        while current:
            if current.student_name == session['username']:
                user_appointments.append((professor, current.time_slot))
            current = current.next

    available_slots = {}
    for professor, details in professors.items():
        booked_slots = set()
        current = details['appointments'].head
        while current:
            booked_slots.add(current.time_slot.lower())
            current = current.next
        available_slots[professor] = [
            slot for slot in details['schedule'] if slot.lower() not in booked_slots
        ]

    return render_template('index.html',
                           professors=professors,
                           available_slots=available_slots,
                           user_appointments=user_appointments)

@app.route('/book', methods=['POST'])
@login_required
def book_appointment():
    student_name = session['username']
    professor_name = request.form['professor']
    day = request.form['day'].strip().capitalize()
    time = request.form['time'].strip().upper()

    time_slot = f"{day} {time}"

    valid_slots = [slot.lower() for slot in professors[professor_name]['schedule']]

    if time_slot.lower() not in valid_slots:
        flash(f"Appointment Invalid Time Slot for {student_name} at {time_slot}", "danger")
        return redirect(url_for('index'))

    result = professors[professor_name]['appointments'].book(student_name, time_slot, professors[professor_name]['schedule'])
    flash(f"Appointment {result} for {student_name} at {time_slot}", "success")
    return redirect(url_for('index'))

@app.route('/cancel', methods=['POST'])
@login_required
def cancel_appointment():
    student_name = session['username']
    professor_name = request.form['professor']
    day = request.form['day'].strip().capitalize()
    time = request.form['time'].strip().upper()

    time_slot = f"{day} {time}"

    result = professors[professor_name]['appointments'].cancel(student_name, time_slot, professors[professor_name]['schedule'])
    flash(f"Appointment {result} for {student_name} at {time_slot}", "info")
    return redirect(url_for('index'))


@app.route('/undo_cancel')
@login_required
def undo_cancel():
    student_name = session['username']

    for professor, details in professors.items():
        result = details['appointments'].undo_cancel(student_name, details['schedule'])

        if result.startswith("Undo successful"):
            flash(result, "success")
            return redirect(url_for('index'))
        elif result != "No canceled appointments to undo.":  # only show specific errors
            flash(result, "danger")
            return redirect(url_for('index'))

    flash("No canceled appointments to undo.", "info")
    return redirect(url_for('index'))


@app.route('/appointments')
@login_required
def view_appointments():
    student_name = session['username']  # Get logged-in user's name
    user_appointments = []

    # Check each professor's appointments to find the student's bookings
    for professor, details in professors.items():
        current = details['appointments'].head
        while current:
            if current.student_name == student_name:
                user_appointments.append((professor, current.time_slot))
            current = current.next

    return render_template('appointments.html', user_appointments=user_appointments)

@app.route('/professors')
@login_required
def view_professors():
    return render_template('professors.html', professors=professors)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
