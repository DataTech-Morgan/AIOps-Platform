import re

stopwords = [
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
    'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
    'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
    'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 
    'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 
    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 
    'can', 'will', 'just', 'done', 'should', 'now', 'must', 'be', 'is', 'are', 'am', 
    'was', 'were', 'do', 'does', 'did', 'have', 'has',
    'had', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might',
    'must', 'need', 'get', 'make', 'take', 'provide', 'give', 'use', 'see',
    'know', 'help', 'try', 'look', 'think', 'want', 
    
]

def strip_emojis(text):
    re_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return re_pattern.sub(r'',text)


