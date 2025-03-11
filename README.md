# GitHub and Workato Integration

This project automates the process of comparing Workato recipes with GitHub repository contents to ensure synchronization between recipe versions and repository data. It includes functionality for fetching recipes, fetching repository data, and generating reports for discrepancies.

## Features

- **GitHub Authentication**: Authenticate using a GitHub App with JWT and installation tokens.
- **Keeper Secrets Integration**: Securely manage and decrypt configuration data using Keeper Secrets Manager.
- **Workato Integration**: Fetch Workato recipes and assets via the Workato API.
- **Data Comparison**: Compare Workato recipes with GitHub repositories for version mismatches and missing recipes.
- **Reporting**: Generate CSV reports for version mismatches and missing recipes.

## Project Structure

- **`auth.py`**: Handles GitHub authentication using JWT and installation access tokens.
- **`keeper.py`**: Manages secure configuration data using Keeper Secrets Manager.
- **`main.py`**: Main script that orchestrates fetching data, comparing versions, and generating reports.

## Prerequisites

1. **Environment Variables**:
   - `CLIENT_ID`: GitHub App client ID.
   - `workato_key`: API key for Workato.
   - `KEEPER_ENCRYPTION_KEY`: Key to decrypt Keeper Secrets configuration.
   - `KEEPER_CONFIG_FILE_PATH`: Path to the encrypted Keeper Secrets configuration file.

2. **Dependencies**:
   - Python 3.8 or higher.
   - Libraries: Install the dependencies listed in `requirements.txt` (see [Installation](#installation)).

3. **GitHub App Setup**:
   - Create a GitHub App and generate a private key (`key.pem`).
   - Install the GitHub App on the organization where repositories are hosted.

4. **Workato Setup**:
   - Obtain the API key for accessing Workato's assets.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/github-workato-integration.git
   cd github-workato-integration
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add the required variables:
     ```env
     CLIENT_ID=your_client_id
     workato_key=your_workato_api_key
     KEEPER_ENCRYPTION_KEY=your_keeper_encryption_key
     KEEPER_CONFIG_FILE_PATH=/path/to/ksm_config.json
     ```

4. Place the GitHub App private key (`key.pem`) in the project root.

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. The script will:
   - Authenticate with GitHub.
   - Fetch recipes from Workato.
   - Fetch repositories from GitHub.
   - Compare data and generate reports.

3. Output:
   - `version_mismatch.csv`: Contains details of recipes with version mismatches.
   - `missing_recipes.csv`: Lists recipes missing from GitHub repositories.

## Documentation 
- Generating a [JWT](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app#example-using-python-to-generate-a-jwt)
- Generating an [access_token](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)