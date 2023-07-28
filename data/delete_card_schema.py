import weaviate  # type: ignore[import]
import typer
import os

from wasabi import msg  # type: ignore[import]

from dotenv import load_dotenv

load_dotenv("../.env")


def main() -> None:
    msg.divider("Starting schema creation")

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

    if not client.schema.exists("Card"):
        msg.warn(f"Card class does not exist")
        return
    else:
        client.schema.delete_class("Card")
        msg.good(f"Card class deleted")


if __name__ == "__main__":
    typer.run(main)
