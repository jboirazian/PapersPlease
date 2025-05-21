from modules.GoogleScholar import search_google_scholar
from modules.ScihubScraper import download_papers
from modules.ChainlitComponents.Starters import get_starters
import chainlit as cl


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

    if not results:
        await cl.Message("❌ No results found. Try another query.").send()
        return

    elements = []

    print(elements)
    for idx, result in enumerate(results, 1):
        content = f"**{idx}. {result['title']}**\n"
        if result['link']:
            content += f"[Link to paper]({result['link']})\n"
        if result['doi']:
            content += f"DOI: `{result['doi']}`\n"
        content += f"Cited by: {result['cited_by']}\n"
        content += f"Snippet: _{result['snippet'][:200]}..._"

        elements.append(cl.Text(content=content))

    await cl.Message(content="📄 Here are the top results:", elements=elements).send()

    # Ask for download confirmation
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

    # Use the last message's content to get the query again
    query = cl.user_session.get("last_query")
    if not query:
        await cl.Message("Error: No search query found in session.").send()
        return

    results = search_google_scholar(query, pages=1)
    downloaded = download_papers(results)

    if downloaded:
        await cl.Message(f"✅ Downloaded {len(downloaded)} papers to the 'papers/' folder.").send()
    else:
        await cl.Message("⚠️ No papers could be downloaded.").send()


@cl.set_starters
async def set_starters():
    return get_starters(["Acromegaly Strenght","Inflation Argentina","Chia seeds Omega3"])

@cl.on_chat_start
async def on_chat_start():
    pass
