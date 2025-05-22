from modules.GoogleScholar import search_google_scholar
from modules.ScihubScraper import download_papers
from modules.ChainlitComponents.Starters import get_starters
from modules.ChainlitComponents.Papers import paperOverview
from chainlit.input_widget import Slider
import chainlit as cl


@cl.set_starters
async def set_starters():
    return get_starters(["Acromegaly Strength", "Inflation Argentina", "Chia seeds Omega3"])


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

    results = search_google_scholar(search_term, pages=10)
    print(results)
    papersfound=[]
    
    for paper in results:
        papersfound.append(cl.Text(content=paperOverview(paper)))
    
    cl.user_session.set("last_query", results)

    await cl.ElementSidebar.set_title("Papers Found")
    await cl.ElementSidebar.set_elements(papersfound)

    await cl.Message(content=f"Found {len(results)} research papers about that topic").send()

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
        pdf_files = []
        for paper in downloaded:
            # Sending a pdf with the local file path
            pdf_files.append(cl.Pdf(name=paper, display="inline",
                                    path=paper, page=1)
                             )

            await cl.ElementSidebar.set_title("canvas")
            await cl.ElementSidebar.set_elements(pdf_files)

    else:
        await cl.Message("⚠️ No papers could be downloaded.").send()
