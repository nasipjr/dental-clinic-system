# -*- coding: utf-8 -*-
import re
from html.parser import HTMLParser
from html import escape as html_escape
from functools import lru_cache
from utils.translations import translations

# Sort keys by length descending to match longer phrases before shorter ones
sorted_keys = sorted(translations.keys(), key=lambda x: len(x), reverse=True)
trans_lookup = {k.lower(): v for k, v in translations.items()}

# Precompile single combined regex pattern for all keys
escaped_keys = [re.escape(k) for k in sorted_keys if k.strip()]
if escaped_keys:
    combined_pattern_str = r'(?<![a-zA-Z0-9])(' + '|'.join(escaped_keys) + r')(?![a-zA-Z0-9])'
    combined_regex = re.compile(combined_pattern_str, re.IGNORECASE)
else:
    combined_regex = None

# Phone pattern to format phone numbers in RTL mode
phone_pattern = re.compile(r'(\+[\d\s-]{5,18}\d|\b09\d[\d\s-]{4,15}\d)')


def format_phone(match):
    m = match.group(0)
    if m.startswith('\u2066') and m.endswith('\u2069'):
        return m
    return '\u2066' + m + '\u2069'


def _translate_match(match):
    matched_str = match.group(1)
    return trans_lookup.get(matched_str.lower(), matched_str)


@lru_cache(maxsize=4096)
def fast_translate_text(text):
    if not text or not text.strip():
        return text

    if combined_regex:
        text = combined_regex.sub(_translate_match, text)

    # Format phone numbers
    text = phone_pattern.sub(format_phone, text)
    return text


class HTMLTranslator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.skip_stack = 0  # To track script/style/translate=no tags
        self.skip_tags = []

    def translate_text(self, text):
        if not text.strip():
            return text

        leading = re.match(r'^\s*', text).group(0)
        trailing = re.search(r'\s*$', text).group(0)
        middle = text.strip()

        translated_middle = fast_translate_text(middle)
        return leading + translated_middle + trailing

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
    if not html_str:
        return html_str
    translator = HTMLTranslator()
    translator.feed(html_str)
    translator.close()
    return translator.get_translated_html()
