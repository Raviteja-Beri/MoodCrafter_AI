from flask import Flask, render_template, request, redirect, url_for, session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session
model = load_model(r'C:\Users\HP\VS Code Projects\Deep Learning\CNN\MoodCrafter_AI\MoodCrafter_AI.h5')

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}  # Expanded image types

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_emotion(img_path):
    try:
        img = image.load_img(img_path, target_size=(200, 200))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        prediction = model.predict(img_array)
        score = prediction[0][0]
        print(f"Prediction score: {score:.4f}")

        if 0.4 <= score <= 0.6:
            return f"🤔 Not Sure (Confidence too low: {max(score, 1 - score) * 100:.1f}%)"
        elif score < 0.4:
            return f"Happy 😀 ({(1 - score) * 100:.1f}% confidence)"
        else:
            return f"Sad 😔 ({score * 100:.1f}% confidence)"

    except Exception as e:
        return f"Error processing image: {str(e)}"


    except Exception as e:
        return f"Error processing image: {str(e)}"


    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded")
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result = predict_emotion(filepath)
            session['filepath'] = filepath
            session['result'] = result
            return redirect(url_for('show_result'))
        else:
            return render_template('index.html', error="Invalid file format. Use JPG, JPEG, PNG, GIF, BMP, or WebP.")
    return render_template('index.html')

@app.route('/result')
def show_result():
    filepath = session.get('filepath')
    result = session.get('result')
    if not filepath or not result:
        return redirect(url_for('index'))
    return render_template('result.html', filepath=filepath, result=result)

if __name__ == '__main__':
    app.run(debug=True)