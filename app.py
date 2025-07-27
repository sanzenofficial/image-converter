from flask import Flask, request, send_file, render_template_string
from PIL import Image
import io

app = Flask(__name__)

# Map file extensions to proper Pillow format names
format_map = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "avif": "AVIF"  # May not be supported on all systems
}

@app.route('/')
def home():
    # Load the HTML page from file
    with open("index.html", "r") as file:
        return render_template_string(file.read())

@app.route('/convert', methods=['POST'])
def convert_image():
    image_file = request.files['image']
    target_format = request.form['format'].lower()

    if target_format not in format_map:
        return "Unsupported format", 400

    try:
        img = Image.open(image_file)
        output_format = format_map[target_format]

        # Handle transparency for JPEGs
        if output_format == "JPEG":
            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))  # white background
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")
        else:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")

        # Save image to a BytesIO buffer (in-memory file)
        buffer = io.BytesIO()
        img.save(buffer, format=output_format)
        buffer.seek(0)

        filename = f"converted.{target_format}"

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype=f"image/{target_format}"
        )

    except Exception as e:
        return f"Error during conversion: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
