# run_local.py
import subprocess
import sys
import os
import time

DB_PATH = "doubleaction.db"
REQUIREMENTS_FILE = "requirements.txt"
DATABASE_SETUP_SCRIPT = "database_setup.py"
SEED_SCRIPT = "seed_database.py"
APP_SCRIPT = "app.py"

def print_header(message):
    """Prints a styled header message."""
    print("\n" + "="*50)
    print(f"  {message}")
    print("="*50)

def run_command(command):
    """Runs a command and handles potential errors."""
    try:
        print(f"Running command: '{' '.join(command)}'...")
        # Using shell=True for compatibility, especially on Windows
        process = subprocess.Popen(' '.join(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        rc = process.poll()
        if rc != 0:
            print(f"Error: Command '{' '.join(command)}' failed with return code {rc}.")
            sys.exit(1) # Exit if a critical command fails
        print(f"Successfully executed: '{' '.join(command)}'")
        return True
    except FileNotFoundError:
        print(f"Error: Command not found. Is '{command[0]}' installed and in your PATH?")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    """Main function to set up and run the application."""
    print_header("DOUBLE ACTION SYSTEM LAUNCHER")

    # Step 1: Install dependencies from requirements.txt
    print_header("STEP 1: Checking and Installing Dependencies")
    run_command([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])

    # Step 2: Set up the database if it doesn't exist
    print_header("STEP 2: Database Setup")
    if not os.path.exists(DB_PATH):
        print(f"Database file '{DB_PATH}' not found.")
        print("Running database setup and seeding scripts...")
        
        # Run database_setup.py to create schema
        run_command([sys.executable, DATABASE_SETUP_SCRIPT])
        
        # Run seed_database.py to populate data
        run_command([sys.executable, SEED_SCRIPT])
        
        print("Database created and seeded successfully.")
    else:
        print(f"Database '{DB_PATH}' already exists. Skipping setup.")

    # Step 3: Run the Flask application
    print_header("STEP 3: Starting Flask Server")
    print(f"The server is starting. Open your browser and go to:")
    print("http://127.0.0.1:5000/login.html")
    print("Press CTRL+C to stop the server.")
    
    time.sleep(2) # Give user a moment to read the message
    
    run_command([sys.executable, APP_SCRIPT])

if __name__ == "__main__":
    main()