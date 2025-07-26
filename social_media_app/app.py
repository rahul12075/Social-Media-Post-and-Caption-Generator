import random
import httpx
import json
from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, flash
import base64
import asyncio
from functools import wraps


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

EMOJIS = [
    "😀", "😂", "🤣", "😍", "🥰", "😘", "😎", "🤩", "😊", "🙃", "😇", "🥹", "😭", "😡", "😱", "😴", "🎉", "🥳",
    "✨", "💫", "🔥", "💥", "🌟", "🎊", "🎈", "🏆", "🏅", "🎮", "🎵", "🎶", "🎤", "❤️", "💖", "💗", "💓", "💞",
    "💕", "💘", "❣️", "💔", "💙", "💚", "💛", "🧡", "💜", "🙌", "👏", "👌", "👍", "👎", "✌️", "🤞", "🤙", "🙏",
    "🤝", "👊", "🤘", "🖐️", "✋", "🌍", "🌎", "🌏", "🌄", "🌅", "🌈", "🌞", "🌙", "⭐", "🌻", "🌸", "🌼", "🌺",
    "🌴", "🍁", "🍕", "🍔", "🍟", "🌮", "🍣", "🍜", "🍩", "🍪", "🍫", "🧁", "🍓", "🍇", "🍎", "🥭", "🥤", "☕",
    "💪", "🏋️", "🏃", "🏃‍♀️", "🚴", "🏄", "🏊", "🧘", "⚽", "🏀", "🏈", "⚾", "🎾", "🥊", "💡", "💻", "🖥️", "📱",
    "📸", "🔋", "🧠", "🕹️", "🚀", "🛰️", "📡", "🧪", "⚙️", "📊", "📈", "👗", "👚", "👠", "👜", "💄", "💅", "👓",
    "💍", "🕶️", "👒", "🐶", "🐱", "🐼", "🦁", "🐯", "🦊", "🐰", "🐨", "🐸", "🦋", "🐝", "✈️", "🚗", "🚕", "🚙",
    "🚲", "🚢", "🚁", "🗺️", "🧳", "⛺", "🏖️", "🗽", "🏝️", "📅", "📆", "📋", "📌", "📎", "📁", "📂", "🗂️", "🧾",
    "💼", "📈", "📉", "📝", "💰", "💵", "💳", "💸", "🛍️", "🛒", "🎁", "🏷️", "💯", "🆒", "🆕", "🔝", "✔️", "✅",
    "❌", "⚠️", "🔔", "📣", "🧿"
]

OLLAMA_BASE_URL = "http://localhost:11434/api"
OLLAMA_MODEL = "llava"
TIMEOUT = 30.0
MAX_IMAGE_SIZE = (512, 512)
JPEG_QUALITY = 75


async_client = None
loop = None

def init_async():
    global async_client, loop
    
    try:
        if loop is None or loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if async_client is None or async_client.is_closed:
            async_client = httpx.AsyncClient(
                base_url=OLLAMA_BASE_URL,
                timeout=TIMEOUT,
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
            )
    except Exception as e:
        print(f"Error initializing async resources: {e}")
        raise


@app.before_request
def before_request():
    init_async()

@app.teardown_request
def teardown_request(exception=None):
    pass  

@app.teardown_appcontext
def teardown_appcontext(exception=None):
    global async_client, loop
    
    try:
        if async_client is not None:
            if loop is not None and not loop.is_closed():
                loop.run_until_complete(async_client.aclose())
            async_client = None
    except Exception as e:
        print(f"Error during async client cleanup: {e}")
    
    if loop is not None and not loop.is_closed():
        loop.close()
    loop = None

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            init_async()
            if loop is None:
                raise RuntimeError("Event loop not initialized")
            
            return loop.run_until_complete(f(*args, **kwargs))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
            return render_template('index.html',
                app_choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                themes=["travel", "fitness", "food", "tech", "fashion", "art", "music", "business", "other"],
                languages={
                    "en": "English", "es": "Spanish", "fr": "French", "de": "German", "hi": "Hindi",
                    "zh": "Chinese", "ar": "Arabic", "ru": "Russian", "pt": "Portuguese", "ja": "Japanese"
                })
    return wrapper

def compress_image(image: Image.Image) -> Image.Image:
    """Compress and resize the image for faster processing"""
    if image.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
        image = background
    elif image.mode != 'RGB':
        image = image.convert('RGB')
    
    if image.size[0] > MAX_IMAGE_SIZE[0] or image.size[1] > MAX_IMAGE_SIZE[1]:
        image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
    
    return image

async def ollama_generate_async(prompt_text: str, model: str, lang: str, image_bytes_base64: str = None) -> str:
    try:
        base_prompt = f"Social media content in {lang} about: {prompt_text}. Be concise."
        
        payload = {
            "model": model,
            "prompt": base_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_ctx": 2048,
                "num_predict": 128
            }
        }
        
        if image_bytes_base64:
            payload["images"] = [image_bytes_base64]
        
        response = await async_client.post("/generate", json=payload)
        response.raise_for_status()
        
        full_response = ""
        for line in response.text.split('\n'):
            if line.strip():
                try:
                    data = json.loads(line)
                    full_response += data.get('response', '')
                except json.JSONDecodeError:
                    continue
        
        return full_response

    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return ""

async def generate_caption(theme: str, lang: str = "en", image: Image.Image = None, keywords: str = "", app: str = "Instagram", formats: list = None) -> str:
    format_text = ""
    if formats:
        format_text = f" in {', '.join(formats)} style"
    
    prompt = f"Very short {app} caption about '{theme}'{format_text}"
    if keywords:
        prompt += f" (keywords: {keywords})"
    return await ollama_generate_async(prompt, model=OLLAMA_MODEL, lang=lang, image_bytes_base64=None)

async def generate_hashtags(theme: str, lang: str = "en", image: Image.Image = None, keywords: str = "", app: str = "Instagram", formats: list = None) -> list[str]:
    format_text = ""
    if formats:
        format_text = f" in {', '.join(formats)} style"
    
    prompt = f"5-10 {app} hashtags for '{theme}' in {lang}{format_text}"
    if keywords:
        prompt += f" (keywords: {keywords})"
    hashtags_raw = await ollama_generate_async(prompt, model=OLLAMA_MODEL, lang=lang, image_bytes_base64=None)
    return [tag.strip() for tag in hashtags_raw.replace('\n', ' ').split() if tag.startswith("#")][:10]

async def generate_emojis(theme: str, count: int = 5, image: Image.Image = None, keywords: str = "", app: str = "Instagram", lang: str = "en", formats: list = None) -> str:
    format_text = ""
    if formats:
        format_text = f" in {', '.join(formats)} style"
    
    prompt = f"{count} emojis for {app} post about '{theme}' in {lang}{format_text}"
    if keywords:
        prompt += f" (keywords: {keywords})"
    emojis_str = await ollama_generate_async(prompt, model=OLLAMA_MODEL, lang=lang, image_bytes_base64=None)
    return " ".join(char for char in emojis_str if char in EMOJIS)[:20]

async def generate_content(theme: str, lang: str, image: Image.Image, keywords: str, app: str, emoji_count: int, add_hashtags: bool = True, add_emojis: bool = True, formats: list = None):
    image_bytes_base64 = None
    if image:
        compressed_image = compress_image(image)
        with BytesIO() as img_bytes_io:
            compressed_image.save(img_bytes_io, format="JPEG", quality=JPEG_QUALITY)
            image_bytes_base64 = base64.b64encode(img_bytes_io.getvalue()).decode('utf-8')

    common_params = {
        "theme": theme,
        "lang": lang,
        "keywords": keywords,
        "app": app,
        "formats": formats
    }

    tasks = [
        generate_caption(**common_params, image=image),
    ]
    
    if add_hashtags:
        tasks.append(generate_hashtags(**common_params, image=image))
    else:
        tasks.append(asyncio.sleep(0)) 
    
    if add_emojis:
        tasks.append(generate_emojis(**common_params, count=emoji_count, image=image))
    else:
        tasks.append(asyncio.sleep(0))  

    results = await asyncio.gather(*tasks)

    caption = results[0]
    hashtags_list = results[1] if add_hashtags else []
    emojis = results[2] if add_emojis else ""
    
    return caption, hashtags_list, emojis

@app.route('/', methods=['GET', 'POST'])
@async_route
async def index():
    if request.method == 'POST':
        app_choice = request.form['app_choice']
        theme = request.form['theme']
        keywords = request.form['keywords']
        lang = request.form['lang']
        emoji_count = min(int(request.form.get('emoji_count', 5)), 10)
        add_hashtags = 'add_hashtags' in request.form
        add_emojis = 'add_emojis' in request.form
        formats = request.form.getlist('format')
        custom_format = request.form.get('format_custom', '').strip()
        
        if custom_format:
            formats.append(custom_format)
        
        selected_theme = theme if theme != "other" else keywords
        image = None
        uploaded_img_data = None

        if 'uploaded_image' in request.files:
            uploaded_file = request.files['uploaded_image']
            if uploaded_file.filename != '':
                try:
                    image_bytes = uploaded_file.read()
                    image = Image.open(BytesIO(image_bytes))
                    
                    with BytesIO() as output:
                        if image.mode == 'RGBA':
                            image.save(output, format="PNG")
                        else:
                            image.save(output, format="JPEG", quality=85)
                        uploaded_img_data = base64.b64encode(output.getvalue()).decode('utf-8')
                    
                    image = compress_image(image)
                    
                except Exception as e:
                    flash(f"Image error: {e}", 'error')
                    image = None

        if image or selected_theme:
            try:
                caption, hashtags_list, emojis = await asyncio.wait_for(
                    generate_content(
                        selected_theme, lang, image, keywords, app_choice, emoji_count,
                        add_hashtags, add_emojis, formats if formats else None
                    ),
                    timeout=45.0
                )
                return render_template('index.html',
                    caption=caption,
                    hashtags_list=hashtags_list,
                    hashtags_string=" ".join(hashtags_list) if hashtags_list else "",
                    emojis=emojis,
                    uploaded_img_data=uploaded_img_data,
                    app_choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
                    themes=["travel", "fitness", "food", "tech", "fashion", "art", "music", "business", "other"],
                    languages={
                        "en": "English", "es": "Spanish", "fr": "French", "de": "German", "hi": "Hindi",
                        "zh": "Chinese", "ar": "Arabic", "ru": "Russian", "pt": "Portuguese", "ja": "Japanese"
                    },
                    selected_formats=formats)  # Pass selected formats back to template
            except asyncio.TimeoutError:
                flash("Generation took too long. Please try with a simpler request or smaller image.", 'error')
            except Exception as e:
                flash(f"An error occurred during generation: {str(e)}", 'error')

    return render_template('index.html',
        app_choices=["Instagram", "Twitter", "LinkedIn", "Facebook"],
        themes=["travel", "fitness", "food", "tech", "fashion", "art", "music", "business", "other"],
        languages={
            "en": "English", "es": "Spanish", "fr": "French", "de": "German", "hi": "Hindi",
            "zh": "Chinese", "ar": "Arabic", "ru": "Russian", "pt": "Portuguese", "ja": "Japanese"
        },
        hashtags_string="",
        selected_formats=["casual"])  
if __name__ == '__main__':
    print("--- Optimized Social Media Content Generator ---")
    print(f"Using model: '{OLLAMA_MODEL}' with timeout: {TIMEOUT}s")
    print("Starting server...")
    
    # Initialize async resources
    init_async()
    
    try:
        app.run(debug=True, use_reloader=False, port=7860)
    finally:
        # Clean up async resources
        if async_client:
            loop.run_until_complete(async_client.aclose())
        if loop and not loop.is_closed():
            loop.close()