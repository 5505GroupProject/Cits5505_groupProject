import nltk
from nltk import ne_chunk, pos_tag
from nltk.tree import Tree

def download_nltk_resources():
    """
    Download NLTK resources needed for NER
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('taggers/maxent_treebank_pos_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')
    
    try:
        nltk.data.find('chunkers/maxent_ne_chunker')
    except LookupError:
        nltk.download('maxent_ne_chunker')
        
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')

# Initialize NLTK resource download
download_nltk_resources()

def perform_ner_analysis(text):
    """
    Perform Named Entity Recognition (NER) analysis using NLTK
    Returns identified named entities and their types
    
    Parameters:
    text (str): Text to analyze
    
    Returns:
    dict: Dictionary containing named entities and their types
    """
    # Tokenize and POS tag the words
    tokens = nltk.word_tokenize(text)
    pos_tagged = nltk.pos_tag(tokens)
    
    # Apply NER chunking to the POS tagged text
    ne_chunks = nltk.ne_chunk(pos_tagged)
    
    # Extract named entities
    named_entities = []
    
    for chunk in ne_chunks:
        if isinstance(chunk, Tree):
            entity_type = chunk.label()
            entity_text = ' '.join([word for word, tag in chunk.leaves()])
            named_entities.append({
                'text': entity_text,
                'type': entity_type
            })
    
    # Group entities by type
    entity_types = {}
    for entity in named_entities:
        entity_type = entity['type']
        if entity_type not in entity_types:
            entity_types[entity_type] = []
        # Only add unique entities (case-insensitive comparison)
        if entity['text'].lower() not in [e.lower() for e in entity_types[entity_type]]:
            entity_types[entity_type].append(entity['text'])
    
    return {
        'entities': named_entities,
        'entity_types': entity_types
    }