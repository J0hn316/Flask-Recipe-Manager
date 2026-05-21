from pathlib import Path
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from database import add_recipe, create_recipes_table, get_all_recipes

app = Flask(__name__)
UPLOAD_FOLDER = Path(app.root_path) / "static" / "uploads" / "recipe_images"
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

create_recipes_table()


def is_allowed_image(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def save_recipe_image() -> str | None:
    uploaded_file = request.files.get("recipe_image")

    if uploaded_file is None or uploaded_file.filename == "":
        return None

    if not is_allowed_image(uploaded_file.filename):
        return None

    safe_filename = secure_filename(uploaded_file.filename)
    upload_path = app.config["UPLOAD_FOLDER"] / safe_filename

    uploaded_file.save(upload_path)

    return safe_filename


@app.route("/", methods=["GET", "POST"])
def home() -> str:
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        prep_time = request.form.get("prep_time", "").strip()
        cook_time = request.form.get("cook_time", "").strip()
        servings = request.form.get("servings", "").strip()
        ingredients = request.form.get("ingredients", "").strip()
        instructions = request.form.get("instructions", "").strip()

        image_filename = save_recipe_image()

        add_recipe(
            title,
            category,
            prep_time,
            cook_time,
            servings,
            ingredients,
            instructions,
            image_filename,
        )

        return redirect(url_for("home"))

    recipes = get_all_recipes()

    return render_template("index.html", recipes=recipes)
