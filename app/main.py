import requests
import os
from dotenv import load_dotenv
import pprint as pp
import json
import pprint as pp
import base64
import csv
from keeper import Keeper
from auth import GithubAuth
import pprint as pp

Keeper.authorize()  # Keeper.authorize()
secret = Keeper.client.get_secrets(["aAaYT-wjTgEZQuF4TCSO2A"])[
    0
]  # Fetch secret from the Keeper vault
private_key = secret.field("keyPair", single=True)["privateKey"]
client_id = secret.custom_field(
    "Github Client ID", field_type=None, single=True, value=None
)
workato_key = secret.custom_field(
    "Workato Token", field_type=None, single=True, value=None
)

github_auth = GithubAuth(client_id, private_key)  # Initialize the GithubAuth class
jwt = github_auth.get_jwt()  # Get the JWT token
headers = github_auth.authenticate_app(jwt)  # Authenticate the app

org_name = "McKenneys-Integrations"  # Organization name


def generate_csv(version_mismatch, missing_recipes):
    # Write version mismatch data to a CSV file
    with open("version_mismatch.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Recipe Version", "Repo Version"])
        writer.writerow(
            [
                version_mismatch.get("name"),
                version_mismatch.get("recipe_version"),
                version_mismatch.get("repo_version"),
            ]
        )

    # Write missing recipes to a CSV file
    with open("missing_recipes.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name"])
        for recipe in missing_recipes:
            writer.writerow([recipe])


def compare_data(recipes, repos):
    """summary: Compare recipe data with repository data

    Args:
        recipes (list): A list of recipes.
        repos (list): A list of repositories.
    """

    total_data = {}
    missing_recipe = []

    # Match recipe names with repo names
    for recipe in recipes:
        if recipe["name"] in repos["name"] and recipe["version"] != repos["version"]:
            print(
                f"Version Mismatch found for {recipe["name"]} and {repos["name"]}.\nCurrent recipe version: {recipe["version"]}\nCurrent repo version: {repos["version"]}"
            )
            total_data["version_mismatch"] = {
                "name": recipe["name"],
                "recipe_version": recipe["version"],
                "repo_version": repos["version"],
            }
        elif recipe["name"] not in repos["name"]:
            print(f"{recipe["name"]} not found in Github")
            missing_recipe.append(recipe["name"])

    total_data["missing_recipes"] = missing_recipe

    return total_data


def fetch_file_content(headers, repo_name, file_path):
    """Fetch the content of a JSON file in a repository.

    Args:
        repo_name (str): The name of the repository.
        file_path (str): The file path in the repository.

    Returns:
        dict: The parsed JSON content of the file.
    """

    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}"
    response = requests.get(url, headers=headers)
    content = response.json()

    print(f"File Content:\n{pp.pformat(content)}\n")

    try:
        print("Attempting to decode content")
        decoded_content = base64.b64decode(content["content"]).decode(
            "utf-8"
        )  # Decode the content
        return json.loads(decoded_content)  # Parse the JSON content
    except:
        print("Failed to decode content")
        return None


def fetch_contents(headers, repo_name):
    """Fetch the contents of a repository.

    Args:
        org_name (str): The name of the organization.
        repo_name (str): The name of the repository.

    Returns:
        list: A list of JSON data in the repository.
    """

    json_data = None
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents"
    response = requests.get(url, headers=headers)
    content = response.json()

    print(f"Content:\n{pp.pformat(content)}\n")

    for item in content:
        if (
            item["type"] == "file"
            and item["name"].endswith(".json")
            and "recipe" in item["name"]
        ):
            print(f"JSON data found {item["name"]}")
            json_data = fetch_file_content(headers, repo_name, item["path"])

    return json_data


def fetch_repos(headers):
    """
    Fetch repositories from an organization.

    Args:
        org_name (str): The name of the organization.

    Returns:
        list: A list of repository names.
    """

    url = f"https://api.github.com/orgs/{org_name}/repos"
    repo_list = []
    repo_data = {}
    repos = []

    while url:
        response = requests.get(url, headers=headers)  # Fetch the repositories
        repos = response.json()  # Convert the response to JSON

        print(f"Repos:\n{pp.pformat(repos)}\n")

        for repo in repos:
            repo_list.append(repo["name"])

        url = response.links.get("next", {}).get(
            "url"
        )  # Get the URL for the next page of results, if any

    for repo in repo_list:
        content = fetch_contents(headers, repo)

        if content:
            repo_data = {
                "name": content["name"],
                "version": content["version"],
            }

    print(f"Repos:\n{pp.pformat(repos)}\n")  # Print the repositories

    return repo_data


def fetch_recipes():
    """Fetch recipes from Workato

    Returns:
        list: A list of recipes.
    """
    # Workato Configuration
    headers = {
        "Authorization": f"Bearer {workato_key}",
        "Accept": "*/*",
    }

    url = "https://www.workato.com/api/export_manifests/folder_assets"
    response = requests.get(url, headers=headers)
    content = response.json()
    assets = content.get("result", {}).get("assets", [])
    recipe_data = []
    # Iterate over the assets
    for item in assets:
        if item.get("type") == "recipe":
            recipe_data.append(
                {
                    "name": item.get("name"),
                    "version": item.get("version"),
                    "type": item.get("type"),
                }
            )

    return recipe_data


def main():
    """
    Main function to fetch repositories, commits, and commit stats
    """

    recipes = fetch_recipes()  # Fetch recipes

    repos = fetch_repos(headers)  # Fetch repositories

    total_data = compare_data(recipes, repos)
    version_mismatch = total_data.get(
        "version_mismatch", {}
    )  # Extract version mismatch information
    missing_recipes = total_data.get("missing_recipes", [])  # Extract missing recipes

    generate_csv(version_mismatch, missing_recipes)


if __name__ == "__main__":
    main()
