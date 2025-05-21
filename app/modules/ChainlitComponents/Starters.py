import chainlit as cl


def get_starters(research_topic: list):
    starters = []
    for topic in research_topic:
        starters.append(cl.Starter(
            label=topic,
            message=topic,
            icon="/public/paper.svg",
        ))
        
    return starters