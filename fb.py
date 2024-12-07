import requests
import json
import os
import csv
from rich.console import Console
from rich.table import Table

# Constants
ACCESS_TOKEN = "your_access_token_here"  # Replace with your valid access token
API_BASE_URL = "https://graph.facebook.com/v16.0"
OUTPUT_FILE = "facebook_post_shares.json"
CSV_OUTPUT_FILE = "facebook_post_shares.csv"

# Initialize Rich Console
console = Console()

# Utility Functions
def fetch_post_shares(post_id):
    """
    Fetches shares for a Facebook post using the Graph API.
    """
    console.print(f"[bold cyan]Fetching shares for post ID: {post_id}...[/bold cyan]")
    url = f"{API_BASE_URL}/{post_id}/sharedposts"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,from{name,id},created_time",
        "limit": 100,
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        console.print(f"[bold red]Error fetching shares for post ID {post_id}: {response.json()}[/bold red]")
        return None


def extract_shares_data(post_id, data):
    """
    Extracts share data from the API response.
    """
    shares_info = []
    if "data" in data:
        for share in data["data"]:
            shares_info.append({
                "Post ID": post_id,
                "Shared By": share.get("from", {}).get("name", "Unknown"),
                "User ID": share.get("from", {}).get("id", "Unknown"),
                "Shared Time": share.get("created_time", "Unknown"),
            })
    return shares_info


def save_to_json(data, filename):
    """
    Saves extracted data to a JSON file.
    """
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    console.print(f"[bold green]Data successfully saved to {filename}.[/bold green]")


def save_to_csv(data, filename):
    """
    Saves extracted data to a CSV file.
    """
    keys = data[0].keys() if data else []
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    console.print(f"[bold green]Data successfully exported to {filename}.[/bold green]")


def display_data(data):
    """
    Displays the share data in a formatted Rich table.
    """
    if not data:
        console.print("[bold yellow]No shares found to display.[/bold yellow]")
        return

    table = Table(title="Facebook Post Shares", show_lines=True)
    table.add_column("Post ID", justify="center")
    table.add_column("Shared By", justify="center")
    table.add_column("User ID", justify="center")
    table.add_column("Shared Time", justify="center")

    for item in data:
        table.add_row(
            item["Post ID"],
            item["Shared By"],
            item["User ID"],
            item["Shared Time"]
        )
    console.print(table)


def main_menu():
    """
    Displays the main menu and handles user choices.
    """
    while True:
        console.print("\n[bold magenta]--- Facebook Post Share Tracker ---[/bold magenta]")
        console.print("[1] Track Shares for a Post")
        console.print("[2] View Saved Data")
        console.print("[3] Export Data to CSV")
        console.print("[4] Exit")

        choice = input("[bold cyan]Enter your choice: [/bold cyan]").strip()

        if choice == "1":
            track_shares()
        elif choice == "2":
            view_saved_data()
        elif choice == "3":
            export_data_to_csv()
        elif choice == "4":
            console.print("[bold green]Goodbye![/bold green]")
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")


def track_shares():
    """
    Tracks shares for user-provided post IDs.
    """
    post_ids = input("[bold cyan]Enter Facebook Post IDs (comma-separated): [/bold cyan]").strip().split(",")
    all_shares_data = []

    for post_id in post_ids:
        post_id = post_id.strip()
        if not post_id:
            continue

        response = fetch_post_shares(post_id)
        if response:
            shares_data = extract_shares_data(post_id, response)
            all_shares_data.extend(shares_data)

    if all_shares_data:
        save_to_json(all_shares_data, OUTPUT_FILE)
        display_data(all_shares_data)
    else:
        console.print("[bold yellow]No data to save or display.[/bold yellow]")


def view_saved_data():
    """
    Loads and displays data from the saved JSON file.
    """
    if not os.path.exists(OUTPUT_FILE):
        console.print("[bold red]No saved data found.[/bold red]")
        return

    with open(OUTPUT_FILE, "r") as file:
        data = json.load(file)

    if data:
        display_data(data)
    else:
        console.print("[bold yellow]Saved data is empty.[/bold yellow]")


def export_data_to_csv():
    """
    Exports data from JSON file to a CSV file.
    """
    if not os.path.exists(OUTPUT_FILE):
        console.print("[bold red]No saved data found to export.[/bold red]")
        return

    with open(OUTPUT_FILE, "r") as file:
        data = json.load(file)

    if data:
        save_to_csv(data, CSV_OUTPUT_FILE)
    else:
        console.print("[bold yellow]No data to export.[/bold yellow]")


if __name__ == "__main__":
    try:
        os.system("cls" if os.name == "nt" else "clear")
        console.print("[bold magenta]Welcome to the Facebook Post Share Tracker![/bold magenta]")
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
