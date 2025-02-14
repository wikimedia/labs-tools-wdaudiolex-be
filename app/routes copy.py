from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    # Print the list of available templates Flask can find
    print(current_app.jinja_env.list_templates())  # This lists all templates Flask can find

    # Render the index.html template
    return render_template('index.html', title="Welcome to WDAudioLEx")
