from werkzeug.datastructures import FileStorage

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def is_allowed_image(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def is_non_negative_int(value: str) -> bool:
    if not value:
        return True

    try:
        number = int(value)
    except ValueError:
        return False

    return number >= 0


def is_positive_int(value: str) -> bool:
    if not value:
        return True

    try:
        number = int(value)
    except ValueError:
        return False

    return number >= 1


def validate_recipe_input(
    title: str,
    prep_time: str,
    cook_time: str,
    servings: str,
    ingredients: str,
    instructions: str,
    uploaded_file: FileStorage | None,
) -> list[str]:
    errors: list[str] = []

    if not title:
        errors.append("Recipe title is required.")

    if prep_time and not is_non_negative_int(prep_time):
        errors.append("Prep time must be 0 or greater.")

    if cook_time and not is_non_negative_int(cook_time):
        errors.append("Cook time must be 0 or greater.")

    if servings and not is_positive_int(servings):
        errors.append("Servings must be 1 or greater.")

    if not ingredients:
        errors.append("Ingredients are required.")

    if not instructions:
        errors.append("Instructions are required.")

    if uploaded_file and uploaded_file.filename:
        if not is_allowed_image(uploaded_file.filename):
            errors.append("Recipe image must be a PNG, JPG, JPEG, GIF, or WEBP file.")

    return errors
