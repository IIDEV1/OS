import re
from nltk.stem.snowball import SnowballStemmer

# Небольшой фиксированный список служебных слов. Отрицания сохранены.
STOP_WORDS = set("и в во на с со к ко у о об от до по за из а но или что это как так то же бы был была было были быть для при я мы ты вы он она оно они мне меня мой моя мое мои его ее их наш ваш этот эта эти тот та те который которая которые тут там вот уже еще очень просто вообще также чем чтобы когда где потому поэтому только даже ну".split())
assert not ({'не', 'ни', 'нет', 'без'} & STOP_WORDS)
STEMMER = SnowballStemmer('russian')

def clean_text(text):
    text = str(text).lower().replace('ё', 'е')
    tokens = re.findall(r'[а-яa-z]+', text)
    return ' '.join(t for t in tokens if t not in STOP_WORDS)

def stem_text(text):
    return ' '.join(STEMMER.stem(t) for t in clean_text(text).split())
