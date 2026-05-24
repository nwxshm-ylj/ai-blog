from __future__ import annotations

import html
import re


def render_markdown(content: str) -> str:
    try:
        from markdown import Markdown
    except ImportError:
        return _render_fallback_markdown(content)

    renderer = Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "codehilite",
                "guess_lang": False,
                "linenums": False,
            }
        },
        output_format="html5",
    )
    return renderer.convert(content)


def _render_fallback_markdown(content: str) -> str:
    blocks: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    paragraph_lines: list[str] = []
    list_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            text = " ".join(paragraph_lines)
            blocks.append(f"<p>{_render_inline(text)}</p>")
            paragraph_lines.clear()

    def flush_list() -> None:
        if list_lines:
            items = "".join(f"<li>{_render_inline(item)}</li>" for item in list_lines)
            blocks.append(f"<ul>{items}</ul>")
            list_lines.clear()

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                escaped = html.escape("\n".join(code_lines))
                language_class = f" language-{html.escape(code_lang)}" if code_lang else ""
                blocks.append(f'<div class="codehilite"><pre><code class="{language_class}">{escaped}</code></pre></div>')
                code_lines.clear()
                code_lang = ""
                in_code = False
            else:
                flush_paragraph()
                flush_list()
                code_lang = line[3:].strip()
                in_code = True
            continue

        if in_code:
            code_lines.append(raw_line)
            continue

        if not line:
            flush_paragraph()
            flush_list()
            continue

        if line.startswith("# "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h1>{_render_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{_render_inline(line[3:])}</h2>")
        elif line.startswith("- "):
            flush_paragraph()
            list_lines.append(line[2:])
        else:
            flush_list()
            paragraph_lines.append(line)

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def _render_inline(value: str) -> str:
    escaped = html.escape(value)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)

