import re
from pathlib import Path


path = Path("source/ProblemBank.ptx")
text = path.read_text()
tag_re = re.compile(r"<(/?)(section|exercise|statement|solution|p|ol|li|ul|image|latex-image)(?:\s[^>]*)?>")

stack = []
insertions = []
image_end = None
for match in tag_re.finditer(text):
    closing, tag = match.group(1), match.group(2)
    if closing:
        if stack and stack[-1][0] == tag:
            opening_tag, opening_start = stack.pop()
            if tag == "image":
                paragraph_count = sum(item[0] == "p" for item in stack)
                if paragraph_count:
                    insertions.append((opening_start, match.end(), paragraph_count))
    else:
        stack.append((tag, match.start()))

for start, end, paragraph_count in reversed(insertions):
    close = "</p>\n" * paragraph_count
    reopen = "\n<p>" * paragraph_count
    text = text[:start] + close + text[start:end] + reopen + text[end:]

text = text.replace("</p>\n</p>\n<image>", "</p>\n<image>")
text = text.replace("</image>\n<p>\n<p>", "</image>\n<p>")

path.write_text(text)