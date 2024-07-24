from flask import Flask, render_template, jsonify, request
import random
import zipfile
from PIL import Image
import base64
import io
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

AI_ZIP_PATH = "finishedGame/AIProduction.zip"
REAL_ZIP_PATH = "finishedGame/RealProduction.zip"

used_images = set()  # Track used images
ai_count = 0
real_count = 0

def load_random_image():
    global used_images, ai_count, real_count

    max_attempts = 10  # Maximum attempts to find an unused image

    for _ in range(max_attempts):
        # Calculate the probability for selecting AI or real images
        total_images = ai_count + real_count
        if total_images == 0:
            ai_prob = 0.5  # 50% probability initially
        else:
            ai_prob = (real_count - ai_count + total_images) / (2 * total_images)
            ai_prob = max(0.2, min(0.8, ai_prob))  # Limit probability between 20% and 80%

        is_ai_image = random.random() < ai_prob

        zip_path = AI_ZIP_PATH if is_ai_image else REAL_ZIP_PATH

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            image_files = [f for f in zip_ref.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if not image_files:
                continue  # Try again if no images found

            image_file = random.choice(image_files)
            if image_file in used_images:
                continue  # Skip used images

            used_images.add(image_file)  # Mark the image as used
            with zip_ref.open(image_file) as img_file:
                image = Image.open(img_file)
                image = image.convert("RGB")  # Convert image to RGB mode to remove alpha channel
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

            if is_ai_image:
                ai_count += 1
            else:
                real_count += 1

            return img_str, is_ai_image

    return None, None  # Return None if no new image found after max_attempts

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_image', methods=['GET'])
def get_image():
    img_str, is_ai_image = load_random_image()
    if img_str is None:
        return jsonify({'error': 'No new images available'}), 404
    return jsonify({'image': img_str, 'is_ai': is_ai_image})

@app.route('/send_results', methods=['POST'])
def send_results():
    data = request.json
    message = MIMEText(f"Real Images Right: {data['real_right']} Real Images Wrong: {data['real_wrong']}\nFake Images Right: {data['fake_right']} Fake Images Wrong: {data['fake_wrong']}")
    message["Subject"] = "Real V Fake Results"
    message["From"] = "cygnus3119@gmail.com"
    message["To"] = "cygnus3119@gmail.com"
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    key = open("finishedGame/systeminfo.txt", "r")
    s.login('cygnus3119@gmail.com', key.readline().strip())
    key.close()
    s.sendmail("cygnus3119@gmail.com", ["cygnus3119@gmail.com"], message.as_string())
    s.quit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
