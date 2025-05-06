import nltk
from nltk import ne_chunk, pos_tag
from nltk.tree import Tree

def download_nltk_resources():
    """
    下载 NER 所需的 NLTK 资源
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

# 初始化下载NLTK资源
download_nltk_resources()

def perform_ner_analysis(text):
    """
    使用NLTK进行命名实体识别（NER）分析
    返回识别出的命名实体及其类型
    
    参数:
    text (str): 要分析的文本
    
    返回:
    dict: 包含命名实体及其类型的字典
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