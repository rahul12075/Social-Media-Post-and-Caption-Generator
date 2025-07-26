# Social-Media-Post-and-Caption-Generator
📌 Table of Contents
Features

1. Demo

2. Installation

3. Configuration

4. Usage

5. Tech Stack

6. API Reference

7. Contributing

8. License

9. Support

# ✨ Features
Content Generation

1. 📝 AI-powered captions for Instagram, Twitter, LinkedIn, Facebook

2. #️⃣ Relevant hashtag suggestions

3. 😊 Emoji recommendations

4. � Multiple content styles (15+ options)

Advanced Options

1. 🌍 Multilingual support (10+ languages)

2. 🖼️ Image context analysis

3. 📋 One-click copy functionality

4. 🎨 Dark/Light mode ready UI

Technical
1. ⚡ Async processing for fast generation

2. 🖼️ Image compression and optimization

3. 🔒 Secure file handling

4. 📱 Mobile-responsive design

🎥 Demo
Live Demo (Coming Soon)
Note: Requires Ollama backend to be running locally

# 🛠️ Installation
Prerequisites
- Python 3.8+

- Ollama installed (installation guide)

- Node.js (for optional frontend builds)

# Setup

1. Clone the repository:

   git clone https://github.com/yourusername/social-media-generator.git

   cd social-media-generator

2. Install Python dependencies:

   pip install -r requirements.txt
   
3. Set up Ollama:

   ollama pull llava

4. Run the application:

   python app.py

5. Access the app at:
   http://localhost:7860

# ⚙️ Configuration

Modify app.py for these settings:

Setting	        Default	                    Description

OLLAMA_BASE_URL	http://localhost:11434/api	Ollama API endpoint

OLLAMA_MODEL	  llava	                      Model to use

TIMEOUT	        30.0	                      Request timeout in seconds

MAX_IMAGE_SIZE	(512, 512)	                Max image dimensions

JPEG_QUALITY	  75	                        Image compression quality

# 🖥️ Usage
1. Select Platform

-  Choose from Instagram, Twitter, LinkedIn, or Facebook

2. Add Context

-  Select a theme from predefined options

-  OR upload an image (max 5MB)

-  add optional keywords

3. Customize Output

-  Choose language (10+ options)

-  Select content style

-  Set emoji count

-  Toggle hashtags on/off

3. Generate & Copy
   
-  Click "Generate Content" and use the one-click copy buttons

# 🛠️ Tech Stack
1. Backend

-  Python 3 - Core language

-  Flask - Web framework

-  Ollama - AI model integration

-  Pillow - Image processing

-  HTTPx - Async HTTP client

2.Frontend

-  Bootstrap 5 - Responsive UI

-  Vanilla JS - Interactive elements

-  CSS3 - Animations and styling

3. Infrastructure

-  Docker - Containerization

-  GitHub Actions - CI/CD (Coming Soon)

# 📚 API Reference

1. Endpoints POST /generate - Main content generation endpoint

2. GET / - Main application interface

# Contributing

- Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# Support

If you encounter any issues, please open an issue on GitHub
