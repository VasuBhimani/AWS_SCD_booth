import base64
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import threading
import time
import json
import requests
from email.message import EmailMessage
import ssl
import random
import smtplib


from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('loading.html')
#-----------------------------------------------------------------------------------------------
# Save the image locally when the POST request is made


@app.route('/save-image', methods=['POST'])
def save_image():
    data = request.json
    print("Received request data")

    # Extract base64 part of the image
    image_data = data['image'].split(",")[1]  # Assumes data:image/jpeg;base64,xxxx
    image_path = os.path.join('static', 'captured_image.jpg')
    
    # Save the image to the local folder
    with open(image_path, 'wb') as f:
        f.write(base64.b64decode(image_data))
    print(f"Image saved to {image_path}")

    # Prepare API call to Segmind
    api_key = os.getenv("SEGMIND_API_KEY")
    
    url = "https://api.segmind.com/v1/instantid"
    
    # Convert the saved image to base64
    b64_image = to_base64(image_path)  
    print("Image converted to base64")

    themes = ["Neon", "Vibrant color", "Mars", "Snow", "Cyberpunk"]
    app_theme = random.choice(themes)

    # Payload for Segmind API
    payload = {
        "prompt": "photo of a human",
        "face_image": b64_image,
        "negative_prompt": "lowquality, badquality, sketches",
        "style": app_theme,
        "samples": 1,
        "num_inference_steps": 10,
        "guidance_scale": 5,
        "seed": 354849415,
        "identity_strength": 0.8,
        "adapter_strength": 0.8,
        "enhance_face_region": True,
        "base64": False
    }

    headers = {
        'x-api-key': api_key
    }

    # Send the API request
    response = requests.post(url, json=payload, headers=headers)

    print("Sent API request, waiting for response...")
    
    # Check the response content type
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')

        if 'application/json' in content_type:
            # Handle JSON response
            try:
                result = response.json()
                print("API call successful, response received")
                return jsonify({"status": "success", "data": result})
            except ValueError:
                print("Error decoding JSON:", response.text)
                return jsonify({"status": "error", "message": "Invalid JSON response"}), 500
        elif 'image' in content_type:
            # Handle binary image response
            with open('static/processed_image.jpg', 'wb') as img_file:
                img_file.write(response.content)
            print("Image saved as processed_image.jpg")
            print(url_for('output'))  # Check the generated URL

# Create a dictionary with a key-value pair
            data = {
                "status": "image is ready"
            }
            # Write the dictionary to the image.json file
            with open('image.json', 'w') as json_file:
                json.dump(data, json_file)
            print("data write inside image file")
            send_email_with_image() 

            return "Processing complete. Check the output page for results."

# Utility function to convert the saved image to base64
def to_base64(img_path):
    with open(img_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.route('/output')
def output():
    with open('image.json', 'w'):
        pass 
    restart()
    return render_template('output.html')


#------------------------------------------------------------------------------------------------

@app.route('/next_page')
def next_page():
    with open('request.json', 'w') as json_file:
        pass  # This will clear the file without writing anything
    return render_template('loading_animation.html')

#-------------------------------------------------------------------------------------------------

last_received_data = None
email = None

@app.route('/webhook', methods=['POST'])
def webhook():
    global last_received_data
    global email

    data = request.get_json()
    print(last_received_data)
    print(type(last_received_data))

    email = data.get('email')
    if data != last_received_data:
        last_received_data = data
        print(f"Received data: {data}")
        with open('request.json', 'w') as json_file:
            json.dump(data, json_file)

        with open('request.json', 'r') as file:
            data = json.load(file)
            user_no = data["no"]  # Extract the value of "no"
            print("user no is :---------",user_no)
        return jsonify({'status': 'success', 'data': data}), 200
    else:
        # print("Duplicate data received. Ignoring.")
        return jsonify({'status': 'ignored', 'data': data}), 200


@app.route('/get-request-data', methods=['GET'])
def get_request_data():
    try:
        with open('request.json', 'r') as json_file:
            data = json.load(json_file)
        return jsonify(data)
    except FileNotFoundError:
        return ""
    except json.JSONDecodeError:
        return ""

@app.route('/get-request-data2', methods=['GET'])
def get_request_data2():
    try:
        with open('image.json', 'r') as json_file:
            data = json.load(json_file)
        return jsonify(data)
    except FileNotFoundError:
        return ""
    except json.JSONDecodeError:
        return ""        

@app.route('/get-request-data3', methods=['GET'])
def get_request_data3():
    try:
        with open('request.json', 'r') as json_file:
            data = json.load(json_file)
        return jsonify(data)
    except FileNotFoundError:
        return ""
    except json.JSONDecodeError:
        return ""        

@app.route('/home')
def home():
    print("index page showing")
    with open('request.json','w'):
        pass
    return render_template('index.html')

#--------------------------------------------------------------------------------------------------


import smtplib
import ssl
from email.message import EmailMessage
from email.mime.text import MIMEText

# @app.route('/testemail', methods=['POST'])
def send_email_with_image():
    global email
    # Define email sender and receiver\
    email_sender = "aws.scd.charusat@gmail.com"
    email_password = os.getenv("EMAIL_PASSWORD")
    email_receiver = email


    # Set the subject and body of the email
    subject = 'Check your AVATAR'
    body_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Your AI Avatar from the Event</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 0;
      }

      .container {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        background-color: #e3e3e993;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        overflow: hidden;
      }

      .header {
        background: linear-gradient(135deg, rgba(252, 70, 107, 0.6), rgba(63, 94, 251, 0.6));
        color: white;
        padding: 20px;
        text-align: center;
      }

      .header img {
        width: 100%; /* Make the image responsive */
        height: auto; /* Maintain aspect ratio */
        border-radius: 10px 10px 0 0; /* Round top corners */
      }

      .header h1 {
        margin: 0;
        font-size: 24px;
      }

      .content {
        padding: 20px;
        text-align: center;
      }

      .content h2 {
        font-size: 20px;
        color: #333;
      }

      .content p {
        font-size: 16px;
        color: #666;
      }

      .button-container {
        margin: 20px 0;
      }

      .button {
        background: linear-gradient(135deg, rgba(252, 70, 107, 0.6), rgba(63, 94, 251, 0.6));
        color: white;
        padding: 10px 20px;
        text-decoration: none;
        font-size: 16px;
        border-radius: 5px;
        display: inline-block;
      }

      .footer {
        background-color: #f4f4f4;
        padding: 10px;
        text-align: center;
        font-size: 12px;
        color: #999;
      }

      @media screen and (max-width: 600px) {
        .container {
          width: 100%;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <img src="https://awsboothdemo2.s3.amazonaws.com/IMG_7819.PNG" alt="Event Header Image" />   
      </div>
      <div class="content">
        <h2>Your AI Avatar is Ready!</h2>
        <p>
          Hi Attendee<br />
          We're excited to share your AI-generated avatar from the event. Please find the image attached to this email.
        </p>
      </div>

    </div>
  </body>
</html>
"""

    # Create the email message object
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body_html, subtype="html")

    # Attach the image
    with open('static/processed_image.jpg', 'rb') as img_file:
        img_data = img_file.read()
        em.add_attachment(img_data, maintype='image', subtype='jpeg', filename='image.jpg')

    # Add SSL (layer of security) and send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("Email sent successfully!")



#-------------------------------------------------------------------------------------------------------------------------

# @app.route('/restart', methods=['POST'])
def restart():
    # Send a "hi" message to the target application
    target_url = 'http://localhost:5001/restart' 
    # target_url ='http://ec2-13-232-231-111.ap-south-1.compute.amazonaws.com:5001/restart'
    data = {'message': 'hi'}
    response = requests.post(target_url, json=data)

    return 'Message sent!', 200

#--------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(port=5000,debug=True,host="0.0.0.0")
