from modules.GoogleScholar import search_google_scholar
from modules.ScihubScraper import download_papers
from modules.ChainlitComponents.Starters import get_starters
import chainlit as cl
import pandas as pd


@cl.set_starters
async def set_starters():
    return get_starters(["Acromegaly Strenght", "Inflation Argentina", "Chia seeds Omega3"])


@cl.on_chat_start
async def on_chat_start():
    pass


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_message
async def handle_message(message: cl.Message):

    search_term = message.content.strip()

    if not search_term:
        await cl.Message("Please provide a search term.").send()
        return

    await cl.Message(f"🔎 Searching for: **{search_term}**").send()

    results = search_google_scholar(search_term, pages=1)
    cl.user_session.set("last_query", results)

    df = pd.DataFrame(results)

    elements = [cl.Dataframe(data=df, display="inline", name="Dataframe")]

    await cl.Message(content="Here is what i found!", elements=elements).send()

    if not results:
        await cl.Message("❌ No results found. Try another query.").send()
        return

    await cl.Message(
        content="Type `download` or click below to attempt downloading the papers.",
        actions=[
            cl.Action(
                name="download",
                label="📥 Download Papers",
                value="yes",
                payload={}
            )
        ]
    ).send()


@cl.action_callback("download")
async def handle_action(action: cl.Action):
    await cl.Message("⏳ Downloading papers...").send()

    downloaded = download_papers(cl.user_session.get("last_query"))

    if downloaded:
        await cl.Message(f"✅ Downloaded {len(downloaded)} papers to the 'papers/' folder.").send()

        for paper in downloaded:
            # Sending a pdf with the local file path

            elements = [
                cl.Pdf(name=paper, display="inline",
                       path=paper, page=1)
            ]
            # Reminder: The name of the pdf must be in the content of the message
            await cl.Message(content="Look at this local pdf1!", elements=elements).send()

    else:
        await cl.Message("⚠️ No papers could be downloaded.").send()
