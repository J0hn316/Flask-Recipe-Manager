from flask import Flask, redirect, render_template, request, url_for

from database import add_recipe, create_recipes_table, get_all_recipes

app = Flask(__name__)

create_recipes_table()


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

        add_recipe(
            title,
            category,
            prep_time,
            cook_time,
            servings,
            ingredients,
            instructions,
        )

        return redirect(url_for("home"))

    recipes = get_all_recipes()

    return render_template("index.html", recipes=recipes)
