# Social-Media-Post-and-Caption-Generator

A Flask-based web application that generates engaging social media content including captions, hashtags, and emoji suggestions using the Ollama LLaVA model.

Features
📝 Generate captions for various social media platforms (Instagram, Twitter, LinkedIn, Facebook)

#️⃣ Create relevant hashtags for your posts

😊 Add emoji suggestions to make your posts more engaging

🌍 Supports multiple languages

🖼️ Image upload capability for context-aware content generation

🎨 Multiple format styles (casual, professional, academic, etc.)

📋 Copy-to-clipboard functionality for easy sharing

Technologies Used
Python 3

Flask (web framework)

Ollama (LLaVA model)

HTTpx (async HTTP client)

Pillow (image processing)

Bootstrap 5 (frontend framework)

HTML5/CSS3/JavaScript

Installation
Clone the repository:

bash
git clone https://github.com/yourusername/social-media-generator.git
cd social-media-generator
Install Python dependencies:

bash
pip install -r requirements.txt
Set up Ollama:

Install Ollama from ollama.ai

Pull the LLaVA model:

bash
ollama pull llava
Run the application:

bash
python app.py
Access the application at http://localhost:7860

Configuration
You can modify these settings in app.py:

python
OLLAMA_BASE_URL = "http://localhost:11434/api"  # Ollama API endpoint
OLLAMA_MODEL = "llava"                          # Model to use
TIMEOUT = 30.0                                  # Request timeout
MAX_IMAGE_SIZE = (512, 512)                     # Max image dimensions
JPEG_QUALITY = 75                               # Image compression quality
Usage
Select your social media platform

Choose a theme or upload an image

Add optional keywords

Select language and style preferences

Click "Generate Content"

Copy the generated content to your clipboard

Screenshots
https://screenshot.png

License
MIT License

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Support
If you encounter any issues, please open an issue on GitHub.
