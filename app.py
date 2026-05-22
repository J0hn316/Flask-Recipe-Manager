from pathlib import Path
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from database import (
    add_recipe,
    create_recipes_table,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe,
)

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


def delete_recipe_image(filename: str | None) -> None:
    if not filename:
        return

    image_path = app.config["UPLOAD_FOLDER"] / filename

    if image_path.exists() and image_path.is_file():
        image_path.unlink()


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


@app.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id: int) -> str:
    recipe = get_recipe_by_id(recipe_id)

    if recipe is None:
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        prep_time = request.form.get("prep_time", "").strip()
        cook_time = request.form.get("cook_time", "").strip()
        servings = request.form.get("servings", "").strip()
        ingredients = request.form.get("ingredients", "").strip()
        instructions = request.form.get("instructions", "").strip()

        new_image_filename = save_recipe_image()
        image_filename = recipe["image_filename"]

        if new_image_filename is not None:
            delete_recipe_image(recipe["image_filename"])
            image_filename = new_image_filename

        update_recipe(
            recipe_id,
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

    return render_template(
        "edit_recipe.html",
        recipe=recipe,
    )
