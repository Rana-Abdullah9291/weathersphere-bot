import os
import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)  # This allows your Vercel site to safely read data from this server

POMELLI_URL = "https://google.com"

# This holds the latest data in the cloud server's active memory
current_weather = {
    'temperature': '--°C',
    'condition': 'Syncing with Pomelli...',
    'timestamp': 'Never'
}

def background_scraper():
    """Runs completely on its own in the cloud background, pulling data every 10 seconds."""
    global current_weather
    
    # Configure browser settings to run headlessly (invisible, no screen needed)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Fire up the automated browser environment
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(POMELLI_URL)
    time.sleep(6)  # Give Pomelli AI apps enough time to finish rendering text layout elements
    
    while True:
        try:
            # Read all visible text directly from the dashboard view screen
            page_text = driver.find_element(By.TAG_NAME, "body").text
            lines = page_text.split('\n')
            
            temp = '--°C'
            cond = 'Live Tracking'
            
            for line in lines:
                if "°" in line:
                    temp = line.strip()
                elif "Weather" in line or "Sky" in line:
                    cond = line.strip()
            
            # Save the parsed strings straight into cloud storage variables
            current_weather = {
                'temperature': temp,
                'condition': cond,
                'timestamp': time.strftime('%H:%M:%S')
            }
        except Exception as e:
            print(f"Automated background extraction error: {e}")
            
        # Freeze for exactly 10 seconds before initiating the next check loop
        time.sleep(10)

@app.route('/api/weather')
def get_weather():
    """Provides instant JSON access to your website when requested."""
    return jsonify(current_weather)

if __name__ == '__main__':
    # Start the standalone background automation processing thread
    t = threading.Thread(target=background_scraper, daemon=True)
    t.start()
    
    # Bind to cloud infrastructure port values dynamically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
