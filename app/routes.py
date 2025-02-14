from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """
    Home route for the application.

    This route does two things:
    1. Prints the list of templates available to Flask. This is useful for debugging and checking which templates Flask can find in the environment.
    2. Renders the 'index.html' template with a dynamic 'title' variable, which is passed from the route.

    The 'title' variable is used to set the page's title in the HTML head and can also be used within the page content.

    ---
    responses:
        200:
            description: Successfully rendered the index.html template with a dynamic title.
            content:
                text/html:
                    schema:
                        type: string
                        example: "<html> ... Welcome to WDAudioLEx ... </html>"
    """
    # Print the list of available templates Flask can find
    print(current_app.jinja_env.list_templates())  # This lists all templates Flask can find

    # Render the index.html template
    return render_template('index.html', title="Welcome to WDAudioLEx")
