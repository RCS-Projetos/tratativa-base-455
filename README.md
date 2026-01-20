# tratativa-base-455

## Project Overview

`tratativa-base-455` is an automation project designed to interact with a web-based system, retrieve specific reports, and process the extracted data. The primary goal is to automate the login process, navigate to report pages, download report files (specifically "base 156" and "base 455"), and then perform data extraction, transformation, and loading (ETL) into an external API.

## Key Features

- **Web Automation:** Automates user login and navigation within a web system using Selenium.
- **Report Generation & Download:** Navigates to specific report pages, applies filters, and downloads report files. Includes retry mechanisms for robust downloading.
- **File Validation:** Ensures downloaded files are present and correctly identified.
- **Data Extraction & Transformation:** Reads data from downloaded CSV files, renames columns for clarity, parses date/time strings, and extracts relevant information.
- **External API Integration:** Interacts with a backend API to search for existing records (e.g., CTRC - Conhecimento de Transporte Eletrônico) and subsequently creates new records (POST) or updates existing ones (PATCH) in batches.
- **Environment Configuration:** Securely manages sensitive information like login credentials and API endpoints through a `.env` file.

## Project Structure

- `main.py`: The main entry point of the application, orchestrating the entire workflow from browser initialization and login to report processing and data synchronization with the API.
- `functions/`: A directory containing modularized Python scripts for various functionalities:
  - `login.py`: Handles the automated login process to the web system using credentials configured in the `.env` file.
  - `open_chrome.py`: Configures and launches the Chrome WebDriver, managing browser options such as headless mode and download preferences.
  - `validar_arquivos.py`: Provides utility functions to validate and retrieve downloaded files from a specified directory.
  - `tratativa_base_156.py`: Contains logic specific to interacting with and downloading reports from the "base 156" section of the web system.
  - `ctrc.py`: Implements the core business logic for interacting with the external API, including:
    - `searc_ctrcs_registers`: Queries the API for existing CTRC records.
    - `ctrcs_list`: Extracts CTRC keys from processed dataframes.
    - `merge_ctrcs`: Integrates API response data with local report data.
    - `new_ctrcs`: Identifies records for initial creation in the external system.
    - `old_ctrcs`: Identifies records that require updates in the external system.
    - `build_payload`: Constructs the structured JSON payloads for API communication, including data cleaning and mapping.
    - `send_registers`: Manages the batch sending of data (new or updated) to the external API.
- `treatments/`: Contains scripts defining specific data treatment processes:
  - `treatment_455.py`: Manages the interaction with the "base 455" report page, setting filters and initiating the download of the relevant report file.
  - `treatment_file_455.py`: Processes the downloaded "base 455" report file, transforming it into a structured DataFrame and coordinating with `ctrc.py` for API interactions (creating new records or updating existing ones).
- `.env`: Configuration file for environment variables, including sensitive data and URLs.
- `pyproject.toml`: Project metadata and Python dependency management.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/tratativa-base-455.git
    cd tratativa-base-455
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -e .
    ```
    or if using `uv`:
    ```bash
    uv pip install -e .
    ```

## Configuration

Create a `.env` file in the project root with the following variables:

```
# Web System Credentials
CPF="your_cpf"
USUARIO="your_username"
SENHA="your_password"

# API Configuration
BASE_URL="http://your-api-url.com/api"
BATCH_SIZE=100
TIMEOUT=30

# Report URLs
URL_156="http://web-system.com/report/156"
URL_455="http://web-system.com/report/455"

# Other
ATTEMPTS=5
```

## Usage

To run the automation script:

```bash
python main.py
```

The script will open a Chrome browser (or run headless if configured), log into the web system, download and process the specified report, and synchronize the data with the external API.

## Dependencies

The project relies on the following principal Python packages:

- `pandas`: For data manipulation and analysis, especially with DataFrames.
- `selenium`: For web browser automation.
- `webdriver-manager`: To automatically manage browser drivers (e.g., ChromeDriver).
- `requests`: For making HTTP requests to the external API.
- `python-dotenv`: For loading environment variables from `.env` files.
- `aiohttp`, `asyncio`, `ipykernel`, `lxml`, `openpyxl`: Other utilities.
