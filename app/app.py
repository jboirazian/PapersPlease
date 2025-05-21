import os
import time
import random
import requests
from bs4 import BeautifulSoup
from scidownl import scihub_download
import chainlit as cl
from chainlit.input_widget import TextInput
from chainlit.input_widget import Tags
from chainlit import AskUserMessage
from typing import Optional

def search_google_scholar(query, pages=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    all_results = []

    for page in range(pages):
        start = page * 10
        url = f"https://scholar.google.com/scholar?start={start}&q={query}&hl=en&as_sdt=0,5"

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            for item in soup.select('.gs_ri'):
                title_elem = item.select_one('.gs_rt')
                title = title_elem.text
                link = title_elem.a['href'] if title_elem.a else None

                doi = None
                if link and 'doi.org' in link:
                    doi = link.split('doi.org/')[-1]
                elif item.select_one('.gs_fl a[href*="doi"]'):
                    doi_link = item.select_one('.gs_fl a[href*="doi"]')['href']
                    doi = doi_link.split('doi.org/')[-1]

                snippet = item.select_one(
                    '.gs_rs').text if item.select_one('.gs_rs') else ''
                cited_by = item.select_one('.gs_fl a[href*="cites"]')
                cited_by = cited_by.text.split()[2] if cited_by else '0'

                all_results.append({
                    'title': title,
                    'link': link,
                    'doi': doi,
                    'snippet': snippet,
                    'cited_by': cited_by,
                    'page': page + 1
                })

        except Exception as e:
            print(f"Error: {e}")
            break

    return all_results


def download_papers(results, download_dir='papers'):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    downloaded = []

    for result in results:
        title = result['title']
        if title:
            try:
                filepath = f"{download_dir}/{title[:100].strip().replace('/', '-')}.pdf"
                scihub_download(title, paper_type="title", out=filepath)
                downloaded.append(filepath)
            except Exception as e:
                print(f"Failed to download '{title}': {e}")
    return downloaded


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


@cl.on_chat_start
async def on_chat_start():
    pass