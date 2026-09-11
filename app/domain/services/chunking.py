"""Fragmentación de texto para RAG.

Agrupa párrafos completos hasta un tamaño objetivo; solo parte por frases
(nunca a mitad de oración) cuando un párrafo por sí solo es demasiado
grande. Cada fragmento arrastra la cola de frases completas del anterior,
para que una idea partida en el límite siga siendo encontrable desde ambos
lados.
"""

import re

TARGET_SIZE = 900
MAX_SIZE = 1400
OVERLAP = 150
MIN_USEFUL = 60

_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def _split_long_paragraph(paragraph: str) -> list[str]:
    sentences = _SENTENCE.split(paragraph)
    blocks, current = [], ""
    for sentence in sentences:
        if not sentence.strip():
            continue
        if current and len(current) + len(sentence) + 1 > MAX_SIZE:
            blocks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current.strip():
        blocks.append(current.strip())
    return blocks


def _tail(text: str, length: int = OVERLAP) -> str:
    if len(text) <= length:
        return text
    snippet = text[-length:]
    cut = _SENTENCE.search(snippet)
    return snippet[cut.end():].strip() if cut else snippet.strip()


def chunk_text(text: str) -> list[str]:
    if not text or not text.strip():
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    units = []
    for paragraph in paragraphs:
        if len(paragraph) > MAX_SIZE:
            units.extend(_split_long_paragraph(paragraph))
        else:
            units.append(paragraph)

    chunks, current = [], ""
    for unit in units:
        if current and len(current) + len(unit) + 2 > TARGET_SIZE:
            chunks.append(current.strip())
            carry = _tail(current)
            current = f"{carry}\n\n{unit}" if carry else unit
        else:
            current = f"{current}\n\n{unit}".strip() if current else unit

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) >= MIN_USEFUL]
