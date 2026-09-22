import html
import re
import subprocess
from pathlib import Path


source = subprocess.check_output(
    ["git", "show", "pr-1:source/Problem Bank.tex"], text=True
)
section = re.search(
    r"\\section\{What is a function\?\}(.*?)(?=\\section\{)",
    source,
    re.DOTALL,
).group(1)
items = re.split(r"(?m)^\s{2}\\item\s+", section)[1:]


def protect_figures(text):
    figures = []

    def replace(match):
        body = html.escape(match.group(0), quote=False)
        token = f"@@FIGURE{len(figures)}@@"
        figures.append(
            "<figure>\n"
            "  <image>\n"
            f"    <latex-image>{body}</latex-image>\n"
            "  </image>\n"
            "</figure>"
        )
        return token

    text = re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        replace,
        text,
        flags=re.DOTALL,
    )
    return text, figures


def convert(text):
    text, figures = protect_figures(text)
    text = re.sub(r"\\begin\{center\}|\\end\{center\}", "", text)
    text = re.sub(r"\\begin\{solution\}", "<solution><p>", text)
    text = re.sub(r"\\end\{solution\}", "</p></solution>", text)
    text = re.sub(r"\\begin\{enumerate\}", "<ol>", text)
    text = re.sub(r"\\end\{enumerate\}", "</ol>", text)
    text = re.sub(r"(?m)^\s*\\item\s+", "<li>", text)
    text = re.sub(r"(?m)(?=^<li>|^</ol>|^<solution>)", "\n", text)
    text = re.sub(r"(?m)(?=^<li>)", "</li>\n", text)
    text = text.replace("</li>\n<ol>", "<ol>")
    text = text.replace("</li>\n</ol>", "</li>\n</ol>")
    text = re.sub(r"\$([^$\n]+)\$", r"<m>\1</m>", text)
    text = html.escape(text, quote=False)
    for tag in ("ol", "/ol", "li", "/li", "solution", "/solution", "p", "/p"):
        text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>")
    for index, figure in enumerate(figures):
        text = text.replace(f"@@FIGURE{index}@@", figure)
    text = re.sub(r"\\newpage|\\vspace\{[^}]*\}", "", text)
    text = re.sub(r"\\text\{([^{}]*)\}", r"\\text{\1}", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


converted = [
    "  <exercise>\n    <statement>\n      <p>"
    + convert(item)
    + "</p>\n    </statement>\n  </exercise>"
    for item in items
]

Path("ProblemBand.ptx").write_text(
    "<section xml:id=\"sec_problem_band\">\n"
    "  <title>What is a function?</title>\n"
    + "\n\n".join(converted)
    + "\n</section>\n"
)