import random
import articleProcessing
from enum import Enum
import re

import fileLogger
logger = fileLogger.FileLogger(__name__)

class TextType(str, Enum):
    TITLE = 'title'
    SUMMARY = 'summary'
    TEXT = 'text'

def extract_quoted_sentences(text):
    pattern_1 = r'"([^"]*)"'
    pattern_2 = r'»(.*?)«'
    
    # Find all matches of the pattern in the text
    quoted_sentences = re.findall(pattern_1, text) + re.findall(pattern_2, text)
    return quoted_sentences

def enumerate_string_list(list):
    for i in range(len(list)):
        list[i] = str(i) + ': ' + list[i]
    return list

def get_enriched_values():
    return ["Stilmittel", "unbekannt", "Institution", "Songtitel", "Gruppe von Personen", "Videotitel"]

def enrich_persons(persons):
    enriched = persons.copy()
    enriched = enriched + get_enriched_values()
    random.shuffle(enriched)
    return enriched

def remove_elements(list, remove_indexes):
    return [element for index, element in enumerate(list) if index not in remove_indexes]

def remove_nested_quotes(quotes):
    remove_indexes = []
    for i, qi in enumerate(quotes):
        for qj in quotes:
            if qi["zitat"] != qj["zitat"] and qi["zitat"] in qj["zitat"] and qi["sprecher"] in qj["sprecher"]:
                remove_indexes.append(i)
    return remove_elements(quotes, remove_indexes)

def filter_duplicate_quotes(data, element_name='zitat'):
    unique_zitats = {}
    filtered_data = []

    for item in data:
        zitat = item[element_name]
        sprecher = item['sprecher']

        if zitat not in unique_zitats:
            unique_zitats[zitat] = sprecher
            filtered_data.append(item)
        elif unique_zitats[zitat] != sprecher:
            filtered_data.append(item)
    return filtered_data

def get_prompt_is_interview(article):
    return f"""
    Ihre Aufgabe besteht darin, festzustellen, ob es sich bei dem gegebenen Text um ein Interview handelt oder nicht.
    Das Interview hat folgenden Aufbau:
    Sprecher: <text> INTERVIEWER: <text>
    Dieses Muster SPEAKER: <text> INTERVIEWER: <text> wird mehrmals wiederholt.
    Wenn der Text diese Struktur nicht aufweist, handelt es sich nicht um ein Interview.
    Ihre Antwort sollte entweder wahr sein, wenn es sich um ein Interview handelt, oder falsch, wenn dies nicht der Fall ist.

    Text:
    {article}
    """


def get_schema_is_interview():
    return {
    "type": "object",
    "properties": {
        "ist_ein_interview": {
            "type": "boolean"
        }
    },
    "required": ["ist_ein_interview"]
}

def send_is_interview_request(article, model):
    res = articleProcessing.sendChatPrompt('', get_prompt_is_interview(article), responseType="json_object", response_schema=get_schema_is_interview(), model=model)
    
    if res == 'ERROR' or res == 'TIMEOUT_ERROR':
        raise Exception(res + " error occured in send_is_interview_request")
    
    return res["ist_ein_interview"]

# extracts and assigns what interviewee said during the interview 
def extract_interview_quotes(text, names):
    flatten_names = []
    for name in names:
        flatten_names.extend(name.split())
    logger.finfo('flatten_names', flatten_names)
    name_pattern = '|'.join(re.escape(name) + ':' for name in flatten_names)
    
    pattern = re.compile(
        f'(' + name_pattern + f')(.*?)(\n|$)',
        re.DOTALL
    )
    quotes = []
    matches = re.finditer(pattern, text)
    # logger.finfo("matches: ", matches)
    for match in matches:
        # logger.finfo("match: ", match)
        interviewee = match.groups()[0][:-1]
        quote = match.groups()[1].strip()
        # logger.finfo("Quote: ", quote)
        
        interviewee_full_name = interviewee
        potential_names = []
        for name in names:
            if interviewee in name:
                potential_names.append(name)
        if len(potential_names) > 0:
            interviewee_full_name = max(potential_names, key=len)
        
        quotes.append({
            "sprecher": interviewee_full_name,
            "zitat": quote,
            # "text_type": [TextType.TEXT]
        })
    return quotes


def get_prompt_direct_missing_quotes(persons, quotes, article):
    return f"""
    Du bist ein Zitat-Zuweisungs-Assistent.
    Sie erhalten eine Liste mit allen im Text genannten Personen.
    Sie erhalten eine Liste der Personen mit ihren Tätigkeiten im Format „Name: [Liste der Tätigkeiten]“.
    Sie erhalten einen Text mit allen Zitaten.
    Sie erhalten eine Liste mit Zitaten, vor denen jeweils die Zitat-ID steht.
    Ihre Aufgabe besteht darin, die Zitat-ID der Person zuzuordnen, die das Zitat mit der angegebenen ID gesagt hat.
    
    Falls ein Zitat keiner Person zugeordnet werden kann, oder der Sprecher unbekannt ist verwende "unbekannt" als Sprecher.
    Wenn es sich bei dem Zitat um eine offizielle Stellungnahme einer Institution (z. B. Regierung, Universität, Krankenhaus usw.) handelt, verwenden Sie „Institution“ als Sprecher.
    Wenn es sich bei dem Zitat um einen Songtitel handelt, verwenden Sie „Songtitel“ als Sprecher.
    Wenn das Zitat von einer Gruppe von Personen gesprochen wird, verwenden Sie „Gruppe von Personen" als Sprecher.
    Falls ein übergebenes Zitat kein tatsächliches Zitat sondern ein Stilmittel ist verwende "Stilmittel" als Sprecher.
    Ein Zitat ist dann ein Stilmittel wenn die Verwendung von « » Zeichen nicht dazu dient das gesprochene Wort einer Person wiederzugeben, sondern eine Markierung eines besonderen Ausdrucks darstellt.
    Sie sollten für jedes Zitat genau eine Antwort haben.
    
    Ich habe Sie bereits gebeten, diesen Zitaten einen Sprecher zuzuweisen, aber das haben Sie nicht getan. Diese Zitate sind definitiv im vorliegenden Text enthalten.
    
    Weisen Sie nur diesen Zitaten Sprecher zu:
    {quotes}
    
    Der Sprecher sollte nur aus dieser Liste stammen:
    {persons}

    In diesem Text sind Zitate enthalten:
    {article}
    """
    

def get_prompt_direct_quotes(persons, quotes, article):
    return f"""
    Du bist ein Zitat-Zuweisungs-Assistent.
    Sie erhalten eine Liste mit allen im Text genannten Personen.
    Sie erhalten eine Liste der Personen mit ihren Tätigkeiten im Format „Name: [Liste der Tätigkeiten]“.
    Sie erhalten einen Text mit allen Zitaten.
    Sie erhalten eine Liste mit Zitaten, vor denen jeweils die Zitat-ID steht.
    Ihre Aufgabe besteht darin, die Zitat-ID der Person zuzuordnen, die das Zitat mit der angegebenen ID gesagt hat.
    
    Falls ein Zitat keiner Person zugeordnet werden kann, oder der Sprecher unbekannt ist verwende "unbekannt" als Sprecher.
    Wenn es sich bei dem Zitat um eine offizielle Stellungnahme einer Institution (z. B. Regierung, Universität, Krankenhaus usw.) handelt, verwenden Sie „Institution“ als Sprecher.
    Wenn es sich bei dem Zitat um einen Songtitel handelt, verwenden Sie „Songtitel“ als Sprecher.
    Wenn das Zitat von einer Gruppe von Personen gesprochen wird, verwenden Sie „Gruppe von Personen" als Sprecher.
    Falls ein übergebenes Zitat kein tatsächliches Zitat sondern ein Stilmittel ist verwende "Stilmittel" als Sprecher.
    Ein Zitat ist dann ein Stilmittel wenn die Verwendung von « » Zeichen nicht dazu dient das gesprochene Wort einer Person wiederzugeben, sondern eine Markierung eines besonderen Ausdrucks darstellt.
    Sie sollten für jedes Zitat genau eine Antwort haben.
    
    Der Sprecher sollte nur aus dieser Liste stammen:
    {persons}
    
    Liste der Zitate:
    {quotes}
    
    Text:
    {article}
    
    """


def get_schema_direct_quotes(persons):
    return {
        "type": "object",
        "required": ["zitate"],
        "properties": {
            "zitate": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "zitat-id": {
                            "type": "number"
                        },
                        "sprecher": {
                            "type": "string",
                            "enum": persons
                        },
                    },
                    "required": ["zitat-id", "sprecher"]
                }
            }
        }
    }

def get_instructions_direct_quotes():
    return f"""
    Setzen Sie Zitate in Ihrer Antwort nicht in Anführungszeichen
    Antworte auf Deutsch.
    """

def send_direct_quotes_request_v2(title, summary, text, names, model):
    try:
        element_name='zitat-id'
        hp = {'temperature': 0, 'top_p': 0.95, 'top_k': 40}
        
        enriched_names = enrich_persons(names)
        
        combined_text = title + '\n' + summary + '\n' + text
        extracted_quotes = extract_quoted_sentences(combined_text)
        
        # for i in range(len(extracted_quotes)):
        #     if extracted_quotes[i][-1] in ['.', '?', '!', ';']:
        #         extracted_quotes[i] = extracted_quotes[i][:-1]
        
        extracted_quotes = enumerate_string_list(extracted_quotes)
            
        # logger.finfo("Quotes:", extracted_quotes)
        # logger.finfo()
        counter = 0
        missing_quotes = []
        final_res = []
        isInterview = False
        
        interview_quotes = []
        if send_is_interview_request(text, model):
            interview_quotes = extract_interview_quotes(text, names=names)
            isInterview = True
        
        while counter < 2:
            if counter > 0:
                quotes = missing_quotes
            else:
                quotes = extracted_quotes
            
            if len(quotes) == 0:
                break
            
            res = []
            indexes = []
            for quote in quotes:
                indexes.append(int(quote.split(": ", 1)[0]))
            if counter > 0:
                direct_quotes_prompt = get_prompt_direct_missing_quotes(enriched_names, quotes, combined_text)
            else:
                direct_quotes_prompt = get_prompt_direct_quotes(enriched_names, quotes, combined_text)
            
            response_res = articleProcessing.sendChatPrompt(get_instructions_direct_quotes(), direct_quotes_prompt, 
                    temperature=hp['temperature'], top_p=hp['top_p'], top_k=hp['top_k'], 
                    responseType="json_object", response_schema=get_schema_direct_quotes(enriched_names), model=model)
            if response_res == "TIMEOUT_ERROR" or response_res == "ERROR":
                return response_res
            
            logger.finfo('response_res', response_res)
            res = response_res['zitate']    
            res = filter_duplicate_quotes(res, element_name=element_name)
            final_res += res
            
            # logger.finfo("x_before_missing_quotes")
            
            if counter > 1:
                break
            
            missing_quotes = []
            for q in quotes:
                match = False
                for rq in res: #rq - resulting quotes
                    quote_text = ''
                    quote_index = rq[element_name]
                    if quote_index > -1 and quote_index < len(extracted_quotes):
                        quote_text = extracted_quotes[quote_index]
                    
                    if q == quote_text:
                        match = True
                if not match:
                    missing_quotes.append(q)
            if len(missing_quotes) == 0:
                break
            
            # logger.finfo("x_after_missing_quotes")
            counter += 1
            
        final_res = filter_duplicate_quotes(final_res, element_name=element_name)
        # logger.finfo("x_after_filter_duplicate")
        remove_indexes = []
        for i, quote in enumerate(final_res):
            quote_index = quote[element_name]
            if quote_index < 0 or quote_index >= len(extracted_quotes):
                remove_indexes.append(i)
        
        final_res = remove_elements(final_res, remove_indexes)
        
        # logger.finfo('final_res', final_res)
        
        for i in range(len(final_res)):
            quote_index = final_res[i][element_name]
            quote_text = ''
            
            if quote_index > -1 and quote_index < len(extracted_quotes):
                quote_text = extracted_quotes[quote_index].split(": ", 1)[1]
            if quote_text != '':
                final_res[i]['zitat'] = quote_text
            else:
                final_res[i]['zitat'] = str(quote_index)
        
        final_res += interview_quotes
        final_res = filter_duplicate_quotes(final_res)
        
        # logger.finfo("before_nested_removal", final_res)
        final_res = remove_nested_quotes(final_res)
        # logger.finfo("after_nested_removal", final_res)
        
        # logger.finfo("final_res", final_res)
        
        for i, quote in enumerate(final_res):
            sentence = quote['zitat']
            final_res[i]["text_type"] = []
            if sentence in title:
                final_res[i]["text_type"].append(TextType.TITLE)
            if sentence in summary:
                final_res[i]["text_type"].append(TextType.SUMMARY)
            if sentence in text:
                final_res[i]["text_type"].append(TextType.TEXT)
        
        result = []
        
        persons = {}
        enriched_values = get_enriched_values()
        
        for name in names:
            persons[name] = {
                'quotedInTitle': False,
                'quotedInIntro': False,
                'directQuotes': [],
            }
        
        for predicted_q in final_res:
            speaker = predicted_q['sprecher']
            if speaker not in enriched_values:
                if speaker not in persons:
                    persons[speaker] = {
                        'quotedInTitle': False,
                        'quotedInIntro': False,
                        'directQuotes': [],
                    }
                persons[speaker]["directQuotes"].append({
                    "text": predicted_q['zitat']
                })
                if "text_type" in predicted_q:
                    if TextType.TITLE in predicted_q["text_type"]:
                        persons[speaker]["quotedInTitle"] = True
                    if TextType.SUMMARY in predicted_q["text_type"]:
                        persons[speaker]["quotedInIntro"] = True
                    
        for name, rest in persons.items():
            result.append({
                "name": name,
                **rest
            })
        
        return {
            "isInterview": isInterview,
            "result": result
        }
    except Exception as e:
        logger.finfo('send_direct_quotes_request exception: ', e.with_traceback())
        return None