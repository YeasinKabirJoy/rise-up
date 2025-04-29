#Setup Instructions

This README provides step-by-step instructions to set up and run the project.

## Prerequisites
- Python 3.8 or higher
- Git
- virtualenv

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YeasinKabirJoy/rise-up.git
   cd rise-up
   ```

2. **Create a Virtual Environment**
   ```bash
   virtualenv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the Project**
   - Open `config.json` in the project root directory.
   - Update the `working_directory` with your project's working directory path in the format `D:/Projects/Assignment/`.
   - Example `config.json`:
     ```json
     {
         "working_directory": "D:/Projects/Assignment/",
         "paths": {
           "image": "assets/men-casual--lifestyle/",
           "csv": "csv/"
         },
         "parameters": {
           "timeout": 10,
           "target_url": "https://www.amarbay.com/product/categories?category=men%20casual-2448"
         }
     }
     ```

6. **Run the Project**
   ```bash
   python main.py
   ```

## Notes
- Ensure the virtual environment is activated before running the project.
- Verify that the `working_directory` path in `config.json` is correct and accessible.