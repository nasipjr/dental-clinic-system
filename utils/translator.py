# -*- coding: utf-8 -*-
import re
from html.parser import HTMLParser
from html import escape as html_escape
from utils.translations import translations

# Sort keys by length descending to match longer phrases before shorter ones
sorted_keys = sorted(translations.keys(), key=lambda x: len(x), reverse=True)

# Precompile regex pattern for each key
# Match the key only if it is not surrounded by alphanumeric characters (similar to safeReplace JS logic)
compiled_patterns = []
for key in sorted_keys:
    escaped_key = re.escape(key)
    pattern = re.compile(rf'(?<![a-zA-Z0-9]){escaped_key}(?![a-zA-Z0-9])', re.IGNORECASE)
    compiled_patterns.append((pattern, translations[key]))

# Phone pattern to format phone numbers in RTL mode
phone_pattern = re.compile(r'(\+[\d\s-]{5,18}\d|\b09\d[\d\s-]{4,15}\d)')

def format_phone(match):
    m = match.group(0)
    if m.startswith('\u2066') and m.endswith('\u2069'):
        return m
    return '\u2066' + m + '\u2069'


class HTMLTranslator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.skip_stack = 0  # To track script/style/translate=no tags
        self.skip_tags = []

    def translate_text(self, text):
        if not text.strip():
            return text
        
        # Extract leading and trailing whitespace
        leading = re.match(r'^\s*', text).group(0)
        trailing = re.search(r'\s*$', text).group(0)
        
        middle = text.strip()
        # Normalize middle whitespace
        normalized_middle = re.sub(r'\s+', ' ', middle)
        
        # Apply translation patterns on normalized middle
        translated = normalized_middle
        for pattern, translation in compiled_patterns:
            translated = pattern.sub(translation, translated)
            
        if translated != normalized_middle:
            return leading + translated + trailing
            
        # Fallback to direct matching on original text if no translation was applied
        for pattern, translation in compiled_patterns:
            text = pattern.sub(translation, text)
            
        # Format phone numbers
        text = phone_pattern.sub(format_phone, text)
        return text

    def handle_starttag(self, tag, attrs):
        self.output.append(f"<{tag}")
        
        is_no_translate = (
            tag.lower() in ('script', 'style') or
            any(name.lower() == 'translate' and value == 'no' for name, value in attrs) or
            any(name.lower() == 'class' and 'notranslate' in (value or '').split() for name, value in attrs)
        )
        if is_no_translate:
            self.skip_stack += 1
            self.skip_tags.append(tag.lower())

        for name, value in attrs:
            if value is not None:
                # Translate specific interactive attributes
                if self.skip_stack == 0 and name.lower() in ('placeholder', 'title', 'data-tooltip', 'data-bs-title', 'data-original-title'):
                    value = self.translate_text(value)
                self.output.append(f' {name}="{html_escape(value)}"')
            else:
                self.output.append(f' {name}')
        self.output.append(">")

    def handle_endtag(self, tag):
        if self.skip_tags and self.skip_tags[-1] == tag.lower():
            self.skip_tags.pop()
            self.skip_stack = max(0, self.skip_stack - 1)
        elif tag.lower() in ('script', 'style'):
            self.skip_stack = max(0, self.skip_stack - 1)
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        if self.skip_stack == 0:
            self.output.append(self.translate_text(data))
        else:
            self.output.append(data)

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")
        
    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")
        
    def handle_pi(self, data):
        self.output.append(f"<?{data}>")

    def get_translated_html(self):
        return "".join(self.output)


def translate_html(html_str):
    translator = HTMLTranslator()
    translator.feed(html_str)
    translator.close()
    return translator.get_translated_html()
