from flask import Flask, render_template, request, jsonify
import requests
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ensure the templates directory exists
os.makedirs('templates', exist_ok=True)

# Create the HTML template file with fixed JavaScript
with open('templates/index.html', 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logo Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-container {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea, select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .checkbox-container {
            display: flex;
            align-items: center;
            margin-top: 15px;
        }
        .checkbox-container input {
            width: auto;
            margin-right: 10px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #2980b9;
        }
        #loading {
            text-align: center;
            margin-top: 20px;
            display: none;
        }
        #result {
            margin-top: 30px;
            text-align: center;
            display: none;
        }
        .logo-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        .logo-item {
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            background-color: white;
        }
        .logo-item img {
            max-width: 200px;
            height: auto;
            display: block;
            margin-bottom: 10px;
        }
        .download-btn {
            background-color: #2ecc71;
            padding: 5px 10px;
            font-size: 14px;
            margin-top: 5px;
        }
        .download-btn:hover {
            background-color: #27ae60;
        }
        .error {
            color: #e74c3c;
            margin-top: 10px;
            text-align: center;
            font-weight: bold;
        }
        .debug-info {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            display: none;
        }
    </style>
</head>
<body>
    <h1>AI Logo Generator</h1>
    
    <div class="form-container">
        <div class="form-group">
            <label for="company_name">Company Name:</label>
            <input type="text" id="company_name" placeholder="Enter your company name">
        </div>
        
        <div class="form-group">
            <label for="company_focus">Company Focus/Industry:</label>
            <input type="text" id="company_focus" placeholder="E.g., technology, food, healthcare, etc.">
        </div>
        
        <div class="form-group">
            <label for="style">Logo Style:</label>
            <select id="style">
                <option value="minimalist">Minimalist</option>
                <option value="modern">Modern</option>
                <option value="vintage">Vintage</option>
                <option value="abstract">Abstract</option>
                <option value="geometric">Geometric</option>
                <option value="playful">Playful</option>
                <option value="professional">Professional</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="colors">Color Preferences:</label>
            <input type="text" id="colors" placeholder="E.g., blue and white, vibrant colors, pastel tones, etc.">
        </div>
        
        <div class="checkbox-container">
            <input type="checkbox" id="use_diffusers" checked>
            <label for="use_diffusers">Use AI Image Generation</label>
        </div>
        
        <button id="generate-btn">Generate Logo</button>
    </div>
    
    <div id="loading">Generating your logo, please wait...</div>
    
    <div id="error-message" class="error"></div>
    
    <div id="result">
        <h2>Generated Logo:</h2>
        <div id="logos-container" class="logo-container"></div>
    </div>
    
    <div id="debug-info" class="debug-info"></div>

    <script>
        // Test backend connectivity on page load
        fetch('http://127.0.0.1:5000/test')
            .then(response => response.json())
            .then(data => {
                console.log('Backend connection test:', data);
            })
            .catch(error => {
                console.error('Backend connection test failed:', error);
                document.getElementById('error-message').textContent = 'Warning: Could not connect to backend server. Make sure it is running at http://127.0.0.1:5000';
            });
    
        document.getElementById('generate-btn').addEventListener('click', function() {
            // Get form values
            const company_name = document.getElementById('company_name').value;
            const company_focus = document.getElementById('company_focus').value;
            const style = document.getElementById('style').value;
            const colors = document.getElementById('colors').value;
            const use_diffusers = document.getElementById('use_diffusers').checked;
            
            // Validate input
            if (!company_name || !company_focus) {
                document.getElementById('error-message').textContent = 'Please fill in company name and focus';
                return;
            }
            
            // Clear previous results and errors
            document.getElementById('error-message').textContent = '';
            document.getElementById('logos-container').innerHTML = '';
            document.getElementById('result').style.display = 'none';
            document.getElementById('debug-info').style.display = 'none';
            
            // Show loading indicator
            document.getElementById('loading').style.display = 'block';
            
            // Log request data for debugging
            const requestData = {
                company_name: company_name,
                company_focus: company_focus,
                style: style,
                colors: colors,
                use_diffusers: use_diffusers
            };
            console.log('Sending request to backend:', requestData);
            
            // Send request to generate logos
            fetch('http://127.0.0.1:5000/generate_logos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                // Hide loading indicator
                document.getElementById('loading').style.display = 'none';
                
                console.log('Received data from backend:', data);
                
                // Show debug info
                const debugElem = document.getElementById('debug-info');
                debugElem.textContent = 'Response: ' + JSON.stringify(data);
                debugElem.style.display = 'block';
                
                if (data.error) {
                    document.getElementById('error-message').textContent = data.error;
                } else {
                    // Display the generated logos
                    const logosContainer = document.getElementById('logos-container');
                    
                    if (data.image_base64) {
                        // Display base64 image
                        const logoItem = document.createElement('div');
                        logoItem.className = 'logo-item';
                        
                        const img = document.createElement('img');
                        img.src = data.image_base64;
                        img.alt = 'Generated Logo';
                        
                        const downloadBtn = document.createElement('button');
                        downloadBtn.className = 'download-btn';
                        downloadBtn.textContent = 'Download Logo';
                        downloadBtn.onclick = function() {
                            const link = document.createElement('a');
                            link.href = data.image_base64;
                            link.download = company_name + '_logo.png';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        };
                        
                        logoItem.appendChild(img);
                        logoItem.appendChild(downloadBtn);
                        logosContainer.appendChild(logoItem);
                    } else if (data.logo_urls && data.logo_urls.length > 0) {
                        // Display URLs from API
                        data.logo_urls.forEach((url, index) => {
                            const logoItem = document.createElement('div');
                            logoItem.className = 'logo-item';
                            
                            const img = document.createElement('img');
                            img.src = url;
                            img.alt = 'Logo Option ' + (index + 1);
                            
                            const downloadBtn = document.createElement('button');
                            downloadBtn.className = 'download-btn';
                            downloadBtn.textContent = 'Download Logo';
                            downloadBtn.onclick = function() {
                                window.open(url, '_blank');
                            };
                            
                            logoItem.appendChild(img);
                            logoItem.appendChild(downloadBtn);
                            logosContainer.appendChild(logoItem);
                        });
                    } else {
                        document.getElementById('error-message').textContent = 'No logo was generated. Please try again.';
                    }
                    
                    document.getElementById('result').style.display = 'block';
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                console.error('Error:', error);
                document.getElementById('error-message').textContent = 'Error connecting to backend server: ' + error.message;
            });
        });
    </script>
</body>
</html>
    ''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-logos', methods=['POST'])
def generate_logos():
    data = request.json
    logger.info(f"Forwarding request to backend: {data}")
    
    # Make a request to the backend API with error handling
    try:
        logger.debug("Sending request to backend")
        response = requests.post(
            'http://127.0.0.1:5000/generate_logos',
            json=data,
            timeout=30
        )
        
        logger.debug(f"Backend response status: {response.status_code}")
        logger.debug(f"Backend response content: {response.content[:500]}...")  # Log first 500 chars
        
        return jsonify(response.json())
    except requests.exceptions.ConnectionError:
        logger.error("Connection to backend failed")
        return jsonify({"error": "Could not connect to backend server. Is it running?"}), 500
    except Exception as e:
        logger.error(f"Error proxying request: {e}")
        return jsonify({"error": str(e)}), 500

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "Frontend server is running"}), 200

if __name__ == '__main__':
    logger.info("Frontend server starting on http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000, debug=True)
