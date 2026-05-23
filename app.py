import os
from uuid import uuid4
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Flask, flash, redirect, render_template, request, url_for


from validators import ALLOWED_IMAGE_EXTENSIONS, validate_recipe_input
from database import (
    add_recipe,
    create_recipes_table,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe,
    delete_recipe,
)

app = Flask(__name__)
UPLOAD_FOLDER = Path(app.root_path) / "static" / "uploads" / "recipe_images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-me",
)

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

create_recipes_table()


def save_recipe_image(uploaded_file: FileStorage | None) -> str | None:
    if uploaded_file is None or uploaded_file.filename == "":
        return None

    safe_filename = secure_filename(uploaded_file.filename)
    file_extension = safe_filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid4().hex}.{file_extension}"

    upload_path = app.config["UPLOAD_FOLDER"] / unique_filename
    uploaded_file.save(upload_path)

    return unique_filename


def delete_recipe_image(filename: str | None) -> None:
    if not filename:
        return

    image_path = app.config["UPLOAD_FOLDER"] / filename

    if image_path.exists() and image_path.is_file():
        image_path.unlink()


@app.route("/", methods=["GET", "POST"])
def home() -> str:
    form_data = {
        "title": "",
        "category": "",
        "prep_time": "",
        "cook_time": "",
        "servings": "",
        "ingredients": "",
        "instructions": "",
    }
    validation_errors: list[str] = []

    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "category": request.form.get("category", "").strip(),
            "prep_time": request.form.get("prep_time", "").strip(),
            "cook_time": request.form.get("cook_time", "").strip(),
            "servings": request.form.get("servings", "").strip(),
            "ingredients": request.form.get("ingredients", "").strip(),
            "instructions": request.form.get("instructions", "").strip(),
        }

        uploaded_file = request.files.get("recipe_image")

        validation_errors = validate_recipe_input(
            form_data["title"],
            form_data["prep_time"],
            form_data["cook_time"],
            form_data["servings"],
            form_data["ingredients"],
            form_data["instructions"],
            uploaded_file,
        )

        if not validation_errors:
            image_filename = save_recipe_image(uploaded_file)

            add_recipe(
                form_data["title"],
                form_data["category"],
                form_data["prep_time"],
                form_data["cook_time"],
                form_data["servings"],
                form_data["ingredients"],
                form_data["instructions"],
                image_filename,
            )

            flash("Recipe added successfully.", "success")
            return redirect(url_for("home"))

    recipes = get_all_recipes()

    return render_template(
        "index.html",
        recipes=recipes,
        form_data=form_data,
        validation_errors=validation_errors,
    )


@app.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id: int) -> str:
    recipe = get_recipe_by_id(recipe_id)

    if recipe is None:
        flash("Recipe not found.", "error")
        return redirect(url_for("home"))

    form_data = {
        "title": recipe["title"],
        "category": recipe["category"] or "",
        "prep_time": (
            str(recipe["prep_time"]) if recipe["prep_time"] is not None else ""
        ),
        "cook_time": (
            str(recipe["cook_time"]) if recipe["cook_time"] is not None else ""
        ),
        "servings": str(recipe["servings"]) if recipe["servings"] is not None else "",
        "ingredients": recipe["ingredients"],
        "instructions": recipe["instructions"],
    }
    validation_errors: list[str] = []

    if request.method == "POST":
        form_data = {
            "title": request.form.get("title", "").strip(),
            "category": request.form.get("category", "").strip(),
            "prep_time": request.form.get("prep_time", "").strip(),
            "cook_time": request.form.get("cook_time", "").strip(),
            "servings": request.form.get("servings", "").strip(),
            "ingredients": request.form.get("ingredients", "").strip(),
            "instructions": request.form.get("instructions", "").strip(),
        }

        uploaded_file = request.files.get("recipe_image")

        validation_errors = validate_recipe_input(
            form_data["title"],
            form_data["prep_time"],
            form_data["cook_time"],
            form_data["servings"],
            form_data["ingredients"],
            form_data["instructions"],
            uploaded_file,
        )

        if not validation_errors:
            new_image_filename = save_recipe_image(uploaded_file)
            image_filename = recipe["image_filename"]

            if new_image_filename is not None:
                delete_recipe_image(recipe["image_filename"])
                image_filename = new_image_filename

            update_recipe(
                recipe_id,
                form_data["title"],
                form_data["category"],
                form_data["prep_time"],
                form_data["cook_time"],
                form_data["servings"],
                form_data["ingredients"],
                form_data["instructions"],
                image_filename,
            )

            flash("Recipe updated successfully.", "success")
            return redirect(url_for("home"))

    return render_template(
        "edit_recipe.html",
        recipe=recipe,
        form_data=form_data,
        validation_errors=validation_errors,
    )


@app.route("/recipes/<int:recipe_id>/delete", methods=["POST"])
def remove_recipe(recipe_id: int) -> str:
    recipe = get_recipe_by_id(recipe_id)

    if recipe is None:
        flash("Recipe not found.", "error")
        return redirect(url_for("home"))

    delete_recipe_image(recipe["image_filename"])
    delete_recipe(recipe_id)

    flash("Recipe deleted successfully.", "success")
    return redirect(url_for("home"))
