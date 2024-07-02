from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import psycopg2
import bcrypt
from flask_mail import Message
# Initialize Flask application
app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# PostgreSQL connection settings
db_host = 'localhost'
db_name = 'kadoma_cholera'
db_user = 'postgres'
db_password = 'Munashe056'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kjimfish@gmail.com'
app.config['MAIL_PASSWORD'] = 'munashe056'

# Function to create tables if not exists
def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INTEGER NOT NULL,
            gender VARCHAR(10) NOT NULL,
            orp VARCHAR(10) NOT NULL,
            symptoms VARCHAR(500) NOT NULL,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            status VARCHAR(10) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        """
    )
    conn = None
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        for command in commands:
            cursor.execute(command)
        cursor.close()
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
    finally:
        if conn is not None:
            conn.close()

            def get_db_connection():
                conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
                return conn

# Function to insert admin data into database
def insert_admin_data(username, password):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admins (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Error inserting admin data: {e}")
        return False

# Function to fetch admin credentials from database
def fetch_admin(username):
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        return admin  # Returns (id, username, password_hash) or None if not found
    except psycopg2.Error as e:
        print(f"Error fetching admin data: {e}")
        return None

# Function to update admin data in database
def update_admin_data(admin_id, new_username):
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("UPDATE admins SET username = %s WHERE id = %s", (new_username, admin_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Error updating admin data: {e}")
        return False

# Function to delete admin from database
def delete_admin(admin_id):
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Error deleting admin: {e}")
        return False

    @app.route('/view_admins', methods=['GET'])
    def view_admins():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, full_name, email FROM admins')
        admins = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(admins)

# Function to insert person data into database
def insert_person_data(name, age, gender, orp, symptoms, latitude, longitude, status):
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, age, gender, orp, symptoms, latitude, longitude, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (name, age, gender, orp, ', '.join(symptoms), latitude, longitude, status))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Error inserting person data: {e}")
        return False
@app.route('/send_diagnosis_email', methods=['POST'])
def send_diagnosis_email():
    patient_name = request.form['patient_name']

    # Compose the email message
    msg = Message('Cholera Diagnosis Notification',
                  sender='kjimfish@gmail.com',
                  recipients=['jfish4835@gmail.com'])

    msg.body = f"A patient has been diagnosed with cholera. Please take necessary actions."




    # Send the email
    try:
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Error sending email: {str(e)}', 500
# Function to fetch admins list from database
def get_admins_list():
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM admins")
        admins = cursor.fetchall()
        cursor.close()
        conn.close()

        admins_list = [{'id': admin[0], 'username': admin[1]} for admin in admins]
        return admins_list
    except psycopg2.Error as e:
        print("Error fetching admins data:", e)
        return []

# Route: Render welcome page
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Route: Render prediction system page
@app.route('/prediction_system')
def prediction_system():
    return render_template('index.html')

# Route: Handle admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = fetch_admin(username)
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin[2].encode('utf-8')):
            session['admin_logged_in'] = True
            session['admin_id'] = admin[0]  # Store admin ID in session for future use
            return redirect(url_for('admin_panel'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('admin_login.html')

# Route: Render admin panel if logged in
@app.route('/admin_panel')
def admin_panel():
    if session.get('admin_logged_in'):
        admins = get_admins_list()  # Fetch admins list from database
        return render_template('admin.html', admins=admins)
    else:
        return redirect(url_for('admin_login'))

def diagnose_cholera(symptoms):
    cholera_symptoms = {'Fever', 'Diarrhea', 'Dehydration', 'Headache', 'Shock',
                        'Abdominal-cramps', 'low-blood-pressure', 'Nausea'}

    matching_symptoms = set(symptoms) & cholera_symptoms
    if len(matching_symptoms) >= 2:  # Adjust threshold as needed
        return True
    else:
        return False

# @app.route('/diagnose_cholera', methods=['POST'])
# def handle_diagnose_cholera():
#     symptoms = request.form.getlist('symptoms')
#     if diagnose_cholera(symptoms):
#         return "Diagnosis: Cholera. Please prepare an oral rehydration solution (ORS)."
#     else:
#         return "Symptoms do not match cholera."
# Route: Save person data
@app.route('/save_person_and_diagnose', methods=['POST'])
def save_person_and_diagnose():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    orp = request.form['orp']
    symptoms = request.form.getlist('symptoms')
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    # Diagnose cholera
    if diagnose_cholera(symptoms):
        status = "positive"
        diagnosis_result = "Cholera. Please prepare an oral rehydration solution (ORS)."
        send_diagnosis_email()  # Corrected placement of function call
    else:
        status = "negative"
        diagnosis_result = "Symptoms do not match cholera."

    # Save person data and diagnosis result to database
    if insert_person_data(name, age, gender, orp, symptoms, latitude, longitude, status):
        return jsonify({'diagnosis_result': status, 'message': diagnosis_result})
    else:
        return jsonify({'error': 'Error saving person data.'}), 500


# Route: Get list of patients
@app.route('/patients')
def get_patients():
    try:
        conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, gender,orp, latitude, longitude FROM patients WHERE status='positive'")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()

        patients_list = []
        patients_list = []
        for patient in patients:
            patients_list.append({
                'id': patient[0],
                'name': patient[1],
                'age': patient[2],
                'gender': patient[3],
                'orp': patient[4],  # Assuming 'orp' is fetched correctly from the database
                'latitude': float(patient[5]),  # Ensure latitude is float (or numeric) in database
                'longitude': float(patient[6])  # Ensure longitude is float (or numeric) in database
            })

        return jsonify(patients_list)
    except psycopg2.Error as e:
        print("Error fetching patient data:", e)
        return jsonify({"error": "Error fetching patient data."}), 500

# Route: Edit admin
@app.route('/edit_admin', methods=['POST'])
def edit_admin():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE admins SET full_name = %s, email = %s, password = %s WHERE id = %s', (data['full_name'], data['email'], data['password'], data['adminId']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Admin updated successfully'})

# Route: Delete admin
@app.route('/delete_admin', methods=['POST'])
def delete_admin():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE id = %s', (data['adminId'],))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Admin deleted successfully'})

# Route: Render admin dashboard
@app.route('/admins')
def admins():
    if session.get('admin_logged_in'):
        admins = get_admins_list()  # Fetch admins list from database
        return render_template('admin.html', admins=admins)
    else:
        return redirect(url_for('admin_login'))

if __name__ == '__main__':
    create_tables()  # Create tables if not exists when the application starts
    app.run(debug=True)
