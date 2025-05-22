import chainlit as cl


def paperOverview(result):
    content = f"> ## {result['title']}\n"
    if result['link']:
        content += f"> [Link to paper]({result['link']})\n"
    content += f"> Cited by: {result['cited_by']}\n"
    
    return content
