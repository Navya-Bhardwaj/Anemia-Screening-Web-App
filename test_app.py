from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('home_modern.html')

@app.route('/screening/realtime')
def realtime_screening():
    return render_template('screening_realtime.html')

if __name__ == '__main__':
    print("🚀 Starting simple test server...")
    print("📱 Real-time screening: http://127.0.0.1:5000/screening/realtime")
    print("🏠 Home page: http://127.0.0.1:5000/")
    app.run(debug=True, host='127.0.0.1', port=5000)
