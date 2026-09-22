import re
from pathlib import Path


path = Path("source/ProblemBank.ptx")
text = path.read_text()

empty_paragraph = re.compile(r"<p>\s*</p>", re.DOTALL)
nested_paragraph = re.compile(r"<p>\s*<p>", re.DOTALL)
duplicate_close = re.compile(r"</p>\s*</p>", re.DOTALL)

while True:
    previous = text
    text = empty_paragraph.sub("", text)
    text = nested_paragraph.sub("<p>", text)
    text = duplicate_close.sub("</p>", text)
    if text == previous:
        break

# Remove paragraph closers that have no corresponding paragraph opener.
paragraph_tag = re.compile(r"</?p>")
result = []
depth = 0
cursor = 0
for match in paragraph_tag.finditer(text):
    result.append(text[cursor:match.start()])
    if match.group(0) == "<p>":
        depth += 1
        result.append(match.group(0))
    elif depth:
        depth -= 1
        result.append(match.group(0))
    cursor = match.end()
result.append(text[cursor:])
path.write_text("".join(result))