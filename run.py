import os
from app import create_app

# Print the current working directory to confirm the app is running from the right place
print(f"Current working directory: {os.getcwd()}")

# Create the Flask app
app = create_app()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode
