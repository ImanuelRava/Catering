from flask import Flask, request, jsonify, render_template
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 1. Serve the HTML Page
@app.route('/')
def index():
    return render_template('index.html')

# 2. API Endpoint for Order Submission
@app.route('/api/submit-order', methods=['POST'])
def submit_order():
    try:
        # Check if the post request has the file part
        if 'paymentPhoto' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['paymentPhoto']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Secure the filename and save it
            filename = secure_filename(file.filename)
            # Add a timestamp to prevent overwriting
            unique_filename = f"{int(os.path.getmtime(__file__))}-{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            # Get other form data
            booking_name = request.form.get('bookingName')
            contact = request.form.get('contact')
            school = request.form.get('school')
            class_name = request.form.get('className')
            cart_data = json.loads(request.form.get('cart'))

            # Create a record (saving to a text file for simplicity)
            order_record = {
                'name': booking_name,
                'contact': contact,
                'school': school,
                'class': class_name,
                'photo': unique_filename,
                'cart': cart_data
            }

            with open('orders_log.txt', 'a') as f:
                f.write(json.dumps(order_record) + "\n")

            print(f"Order received from {booking_name}")
            
            return jsonify({'message': 'Order submitted successfully!'}), 200

        else:
            return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)