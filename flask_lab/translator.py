import json
from logging import Logger
import os
from .const import LANGUAGE, ROOT_PATH

RTL = ['il']
ROOT_PATH=os.environ.get("ROOT_PATH", default=ROOT_PATH)
logger = Logger(name=__name__)

class Translator():
    def __init__(self, lang = LANGUAGE) -> None:
        self.lang = lang
        lang_file = f'{ROOT_PATH}/languages/{self.lang}.json'
        self.language_dict = {}
        if os.path.isfile(lang_file):
            with open(lang_file, encoding='utf-8') as file:
                try:
                    self.language_dict = json.load(file)
                    logger.info(self.language_dict)
                except Exception:
                    logger.error(f'Error getting language file {lang_file}', exc_info=True)
        else:
            with open(lang_file, 'x') as file:
                file.write('{}')
    
    def translate(self, text: str, format='') -> str:
        translated_text = []
        if text.lower() in self.language_dict.keys():
            if text_data := self.language_dict.get(text.lower()):
                if format:
                    text_data = text_data.format(format)
            return text_data

        if len(text.split(' ')) > 1:
            for word in text.split(' '):
                if word.lower() in self.language_dict.keys():
                    translated_text.append(self.language_dict.get(word.lower()))
                else:
                    translated_text.append(word)
        else:
            return text
        if self.lang in RTL:
            translated_text.reverse()
        return ' '.join(translated_text)


def lang(text, lang=LANGUAGE, format=''):
    translator = Translator(lang)
    return translator.translate(text, format)

