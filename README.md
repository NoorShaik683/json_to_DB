# json_to_DB

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/NoorShaik683/json_to_DB.git
    cd json_to_DB
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use "venv\Scripts\activate"
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Environment File

Create a `.env` file in the root directory of the project with the following content:

```env
API_ENDPOINT=http://127.0.0.1:5000
DATABASE_FILE_NAME="data.db"

Replace the values with your actual API endpoint and database file name.
```

## Running Flask Code (main.py)

Ensure your virtual environment is activated:

```bash
source venv/bin/activate  # On Windows, use "venv\Scripts\activate"
```

Run the Flask application:

```bash
python main.py
```
The Flask app should be running at http://127.0.0.1:5000.

## Running Streamlit Code (1_🏠_Home.py)

Ensure your Flask application is running.

Open a new terminal and activate the virtual environment:

```bash
source venv/bin/activate  # On Windows, use "venv\Scripts\activate"
```

Run the Streamlit application:

```bash
streamlit run 1_🏠_Home.py
```
The Streamlit app should be accessible in your browser at http://localhost:8501.
