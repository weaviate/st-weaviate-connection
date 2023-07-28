import weaviate  # type: ignore[import]
import typer
import os
import json
import requests
import random

from wasabi import msg  # type: ignore[import]

from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv("../.env")


def get_card_details(card_name) -> dict:
    """Retrieve information from the scryfall API about a card through its name
    @parameter card_name : str - Card name
    @returns dict - A dictionary with the card information formatted to the correct Weaviate schema
    """
    # Construct the URL for the API request
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"

    # Send a GET request to the API
    response = requests.get(url)

    mana_dict = {"W": "White", "B": "Black", "R": "Red", "G": "Green", "U": "Blue"}

    # If the request was successful, the status code will be 200
    if response.status_code == 200:
        # Parse the response as JSON
        card_data = response.json()

        weaviate_object = {
            "name": card_data.get("name", "Unknown"),
            "card_id": str(card_data.get("arena_id", "0")),
            "img": card_data.get("image_uris", {"normal": ""}).get("normal", ""),
            "mana_cost": card_data.get("mana_cost", "0"),
            "type": card_data.get("type_line", ""),
            "mana_produced": str(card_data.get("produced_mana", "")),
            "power": card_data.get("power", "0"),
            "toughness": card_data.get("toughness", "0"),
            "color": str(card_data.get("colors", "")),
            "keyword": str(card_data.get("keywords", "")),
            "set": card_data.get("set_name", ""),
            "rarity": card_data.get("rarity", ""),
            "description": card_data.get("oracle_text", ""),
        }

        for color_code in mana_dict:
            weaviate_object["mana_produced"] = weaviate_object["mana_produced"].replace(
                color_code, mana_dict[color_code]
            )
            weaviate_object["mana_cost"] = weaviate_object["mana_cost"].replace(
                color_code, mana_dict[color_code]
            )
            weaviate_object["color"] = weaviate_object["color"].replace(
                color_code, mana_dict[color_code]
            )
        return weaviate_object

    else:
        return None


def add_card_to_weaviate(weaviate_obj: dict, client: weaviate.Client) -> None:
    """Import a card object to Weaviate
    @parameter weaviate_obj : diuct - Formatted dict with the same keys as the schema
    @parameter client : weaviate.Client - Weaviate Client
    @returns None
    """
    with client.batch as batch:
        batch.batch_size = 1
        client.batch.add_data_object(weaviate_obj, "Card")
        msg.good(f"Imported {weaviate_obj['name']} to database")


def main() -> None:
    msg.divider("Starting card retrieval")

    # Connect to Weaviate
    url = os.environ.get("WEAVIATE_URL", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    auth_config = weaviate.AuthApiKey(api_key=os.environ.get("WEAVIATE_API_KEY", ""))

    if openai_key == "" or url == "":
        msg.fail("Environment Variables not set.")
        msg.warn(f"URL: {url}")
        msg.warn(f"OPENAI API KEY: {openai_key}")
        return

    client = weaviate.Client(
        url=url,
        additional_headers={"X-OpenAI-Api-Key": openai_key},
        auth_client_secret=auth_config,
    )

    msg.good("Client connected to Weaviate Server")

    query_results = (
        client.query.get(
            "Card",
            ["name"],
        )
        .with_limit(30000)
        .do()
    )

    unique_cards = set(
        [
            str(card["name"]).lower().strip()
            for card in query_results["data"]["Get"]["Card"]
        ]
    )

    msg.info(f"Loaded {len(query_results['data']['Get']['Card'])} cards")

    with open("all_cards.json", "r") as reader:
        all_cards = json.load(reader)["data"]

    msg.info(f"{len(all_cards)-len(unique_cards)} Cards left to fetch")

    random.shuffle(all_cards)

    for card_name in tqdm(all_cards):
        if card_name.lower().strip() not in unique_cards:
            card = get_card_details(card_name)
            if card != None:
                add_card_to_weaviate(card, client)
        else:
            msg.info(f"Skipping {card_name}")


if __name__ == "__main__":
    typer.run(main)
