import articleProcessing

import fileLogger
logger = fileLogger.FileLogger(__name__)

system_prompt_occupations = "You are a professional biographer who answers in JSON. I provide you with a text and one specific person."

def prompt_occupations(person, response_format):
    prompt_occupations = f"""
You are tasked with extracting all relevant information regarding the occupations, family status, and opinions of {person} from the provided article. Your job is to:\n\n

- Extract all occupations releated to {person}, including current as well as former job titles (retired jobs), professional roles, businesses owned, career achievements, and what opinions people or the author has about {person} .\n
- Extract all mentions of family status and significant relationships directly relevant to {person}. Do not include something that is not mentioned in the article. This list can also be empty\n
- Extract and list opinions about {person}, capturing exact words and phrases in the article used by others or the author about {person} for the description, do not rephrase it, including positive, neutral, and negative comments. Ensure to include any relevant contextual information or titles (e.g., "politician", "CEO") that describe or categorize {person} in relation to the opinions expressed.
- Ensure that your response includes an exact copy of the words and phrases used in the article, without any interpretation, rephrasing, or omission. If something is not mentioned do not list it. The lists can also be empty. Each element should be listed only once \n
- For each occupation, family status and opinion provide a reason why it was included, supported by a direct quote from the text as evidence.\n

Your response for each element should be one sentence for the reasoning and one sentence for the quote. \n
Always answer in German.
"""
# Always answer in the following structured JSON format:\n\n
# {response_format}
    return prompt_occupations



response_format_occupations_2 = {
    "type": "object",
    "properties": {
        "occupations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "reasoning": {"type": "string"},
                    "quote": {"type": "string"},
                },
                "required": ["description", "reasoning", "quote"],
            },
        },
        "family_status": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "reasoning": {"type": "string"},
                    "quote": {"type": "string"},
                },
                "required": ["description", "reasoning", "quote"],
            },
        },
        "opinions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "reasoning": {"type": "string"},
                    "quote": {"type": "string"},
                },
                "required": ["description", "reasoning", "quote"],
            },
        },
    },
    "required": ["occupations", "family_status", "opinions"],
}

def is_role(description, reasoning, person, article, model):
    userPrompt = f"""Article:\
{article}
description:
{description}

reasoning:
{reasoning}
Is the description correct for {person} with respect to the reasoning. In other words is '{person}' '{description}'. Provide a True or False. Please answer in JSON"""
    result = articleProcessing.sendChatPrompt(
        "You are a helpful assistant.",
        userprompt=userPrompt,
        temperature=0,
        responseType="json_object",
        response_schema={
            "type": "object",
            "properties": {
                "is_role": {"type": "boolean"},
                "reasoning": {"type": "string"},
            },
            "required": ["is_role", "reasoning"],
        },
        model=model,
        promptDescription="OccupationIsRolePrompt"
    )

    return result["is_role"]

def extractOccupations(title, intro, article, personName, model, temperature = 0.1, repeat_penalty = 1, top_p = 0.90, top_k = 40) -> list[str]:
     
    userPrompt = f"""Article:
title:
{title}

intro:
{intro}

text:
{article}

{prompt_occupations(personName, response_format_occupations_2)}"""


    result = articleProcessing.sendChatPrompt( systemprompt=system_prompt_occupations,
                                                            userprompt=userPrompt,
                                                            temperature=temperature,
                                                            responseType="json_object",
                                                            repeat_penalty=repeat_penalty,
                                                            top_p=top_p,
                                                            top_k=top_k,
                                                            response_schema=response_format_occupations_2,
                                                            model=model,
                                                            promptDescription="OccupationRecognitionPrompt");
    logger.finfo(result)
    
    articleText = title + " --- " + intro + " --- " + article

    occupations_tmp = (
        result["occupations"] + result["family_status"] + result["opinions"]
    )
    occupations = []

    for occupation in occupations_tmp:
        description = occupation["description"]
        reasoning = occupation["reasoning"]
        
        if (
            description in articleText
            and any(word[0].isupper() for word in description.split())
            and not any(o["text"] == description for o in occupations)
            and is_role(description, reasoning, personName, articleText, model)
        ):
            occupations.append({"text": occupation["description"]})

    
    return [occ['text'] for occ in occupations]
     