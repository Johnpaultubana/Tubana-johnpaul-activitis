from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'student_info_sys'

SALT = 'qwertyuio123456'

mysql = MySQL(app)

# Route for the login page
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling login logic
@app.route('/check-user', methods=['POST'])
def check_user():
    try:
        username = request.form['username']
        password = request.form['password']

        # Hash the password with the salt
        salted = str(SALT + password).encode('utf-8')
        hashed_password = hashlib.sha512(salted).hexdigest()

        # Query the database for the user
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Store user information in the session
            session['user_id'] = user[0]  # Assuming the first column is the user ID
            session['username'] = user[1]  # Assuming the second column is the username
            return redirect(url_for('home'))
        else:
            return render_template('index.html', error="Invalid Username or Password")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for the home page (dashboard)
@app.route('/home')
def home():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('index'))

    return render_template('home.html')

# Route to fetch all students
@app.route('/get-students', methods=['GET'])
def get_students():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        rows = cur.fetchall()
        cur.close()

        # Convert rows to a list of dictionaries
        students = []
        for row in rows:
            students.append({
                'id': row[0],
                'studentId': row[1],
                'lastName': row[2],
                'middleName': row[3],
                'course': row[4],
                'year': row[5]
            })

        return jsonify(students)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add a student
@app.route('/add-student', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Insert the student into the database
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO student_info (student_id, last_name, middle_name, course, year) VALUES (%s, %s, %s, %s, %s)",
            (data['studentId'], data['lastName'], data.get('middleName', ''), data['course'], data['year'])
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Student added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to update a student
@app.route('/update-student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.get_json()
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE student_info SET student_id = %s, last_name = %s, middle_name = %s, course = %s, year = %s WHERE id = %s",
            (data['studentId'], data['lastName'], data.get('middleName', ''), data['course'], data['year'], student_id)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Student updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to delete a student
@app.route('/delete-student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM student_info WHERE id = %s", (student_id,))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Student deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to add a user (for testing purposes)
@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        # Get username, password, and role from the request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        # Hash the password with the salt
        salted = str(SALT + password).encode('utf-8')
        hashed_password = hashlib.sha512(salted).hexdigest()

        # Insert the user into the database
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'User added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)