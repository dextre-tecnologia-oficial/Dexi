#!/usr/bin/env python3
"""Gera index.html a partir dos arquivos nas pastas do codex."""

from __future__ import annotations

import html
import shutil
from pathlib import Path
from urllib.parse import quote

INDEX_DIR = Path(__file__).resolve().parent
KNOWLEDGE_ROOT = INDEX_DIR.parent

CATEGORIES = [
    {
        "id": "intuitios",
        "folder": "intuitios",
        "aliases": [],
        "title": "Intuitios",
        "subtitle": "Conhecimentos intuitivos",
        "accent": "amber",
        "icon": "✦",
    },
    {
        "id": "linguas",
        "folder": "linguas",
        "aliases": ["linguisticos", "linguagem", "linguagens"],
        "title": "Línguas",
        "subtitle": "Línguas e linguagem",
        "accent": "emerald",
        "icon": "◈",
    },
    {
        "id": "scientias",
        "folder": "scientias",
        "aliases": ["scientia"],
        "title": "Scientias",
        "subtitle": "Conhecimentos científicos",
        "accent": "indigo",
        "icon": "◎",
    },
]

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
AUDIO_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}
PDF_EXT = {".pdf"}
TEXT_EXT = {".txt", ".md", ".markdown", ".log", ".csv"}


def resolve_category_folder(cat: dict, root: Path) -> Path:
    """Resolve a pasta real da categoria, aceitando nomes antigos e novos."""
    for name in [cat["folder"], *cat.get("aliases", [])]:
        candidate = root / name
        if candidate.exists():
            return candidate
    return root / cat["folder"]


def file_kind(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext in IMAGE_EXT:
        return "image"
    if ext in AUDIO_EXT:
        return "audio"
    if ext in PDF_EXT:
        return "pdf"
    if ext in TEXT_EXT:
        return "text"
    return None


def render_file(folder: str, path: Path) -> str:
    rel = f"../{folder}/{quote(path.name)}".replace("\\", "/")
    slug = f"{folder}-{path.stem}".lower().replace(" ", "-")
    name = html.escape(path.name)
    kind = file_kind(path)
    open_link = (
        f'<p class="mt-2 mb-0 text-sm">'
        f'<a href="{html.escape(rel)}" class="link-gold" target="_blank" rel="noopener noreferrer">'
        f'Abrir {name} no navegador</a></p>'
    )

    if kind == "image":
        body = (
            f'<figure class="codex-media">'
            f'<img src="{html.escape(rel)}" alt="{name}" class="img-fluid rounded-3 shadow-sm" loading="lazy">'
            f"<figcaption class=\"mt-2 text-sm text-slate-500\">{name}</figcaption>"
            f"</figure>"
            f"{open_link}"
        )
    elif kind == "audio":
        body = (
            f'<div class="codex-media">'
            f'<p class="mb-2 fw-semibold text-slate-700">{name}</p>'
            f'<audio controls preload="metadata" class="w-100">'
            f'<source src="{html.escape(rel)}">'
            f"Seu navegador não suporta áudio embutido. "
            f'<a href="{html.escape(rel)}">Baixar {name}</a>'
            f"</audio></div>"
            f"{open_link}"
        )
    elif kind == "pdf":
        body = (
            f'<div class="codex-media">'
            f'<p class="mb-2 fw-semibold text-slate-700">{name}</p>'
            f'<embed src="{html.escape(rel)}" type="application/pdf" '
            f'class="codex-pdf rounded-3 shadow-sm" '
            f'title="{name}">'
            f'<p class="mt-2 text-sm">'
            f'<a href="{html.escape(rel)}" class="link-gold" target="_blank" rel="noopener noreferrer">Abrir PDF em nova aba</a>'
            f"</p></div>"
        )
    elif kind == "text":
        raw = path.read_text(encoding="utf-8", errors="replace")
        body = (
            f'<div class="codex-media">'
            f'<p class="mb-2 fw-semibold text-slate-700">{name}</p>'
            f'<pre class="codex-text rounded-3 shadow-sm">{html.escape(raw)}</pre>'
            f"</div>"
            f"{open_link}"
        )
    else:
        return ""

    badge = kind.upper()
    return f"""
    <article id="{slug}" class="codex-entry mb-4">
      <details class="codex-details" open>
        <summary class="codex-summary">
          <span class="codex-badge codex-badge-{kind}">{badge}</span>
          <span class="codex-entry-title">{name}</span>
        </summary>
        <div class="codex-entry-body">{body}</div>
      </details>
    </article>
    """


def render_category(cat: dict) -> tuple[str, str]:
    folder_path = resolve_category_folder(cat, KNOWLEDGE_ROOT)
    folder_path.mkdir(exist_ok=True)

    files = sorted(
        (p for p in folder_path.iterdir() if p.is_file() and file_kind(p)),
        key=lambda p: p.name.lower(),
    )

    nav_links = ""
    entries = ""

    if files:
        for path in files:
            slug = f"{cat['id']}-{path.stem}".lower().replace(" ", "-")
            nav_links += (
                f'<li><a class="codex-nav-link" href="#{slug}">{html.escape(path.name)}</a></li>\n'
            )
            entries += render_file(cat["folder"], path)
    else:
        entries = (
            f'<div class="codex-empty rounded-3 p-4 text-center">'
            f'<p class="mb-1 fw-semibold">Nenhuma nota ainda</p>'
            f'<p class="mb-0 text-sm text-slate-500">'
            f"Adicione imagens, áudios, PDFs ou textos em "
            f'<code>{folder_path.name}/</code> (raiz do projeto) e execute '
            f"<code>python build_codex.py</code>."
            f"</p></div>"
        )

    section = f"""
    <section id="{cat['id']}" class="codex-section codex-section-{cat['accent']} mb-5">
      <header class="codex-section-header mb-4">
        <span class="codex-section-icon" aria-hidden="true">{cat['icon']}</span>
        <div>
          <h2 class="codex-section-title mb-1">{cat['title']}</h2>
          <p class="codex-section-subtitle mb-0">{cat['subtitle']}</p>
        </div>
      </header>
      <nav class="codex-file-nav mb-4" aria-label="Notas em {cat['title']}">
        <p class="codex-file-nav-label">Notas nesta seção</p>
        <ul class="codex-file-list">
          {nav_links if files else '<li class="text-slate-500 text-sm">— vazio —</li>'}
        </ul>
      </nav>
      <div class="codex-entries">
        {entries}
      </div>
    </section>
    """

    nav_item = f"""
    <li>
      <a class="codex-nav-category codex-nav-{cat['accent']}" href="#{cat['id']}">
        <span class="codex-nav-icon">{cat['icon']}</span>
        <span>
          <strong>{cat['title']}</strong>
          <small>{cat['subtitle']}</small>
        </span>
      </a>
    </li>
    """

    return nav_item, section


def migrate_legacy_folders() -> None:
    """Move arquivos de pastas antigas para a pasta preferida da categoria, se existirem."""
    for cat in CATEGORIES:
        target = KNOWLEDGE_ROOT / cat["folder"]
        target.mkdir(exist_ok=True)

        for alias in cat.get("aliases", []):
            legacy = KNOWLEDGE_ROOT / alias
            if not legacy.exists() or legacy.resolve() == target.resolve():
                continue
            for path in legacy.iterdir():
                if not path.is_file():
                    continue
                dest = target / path.name
                if dest.exists():
                    path.unlink()
                else:
                    shutil.move(str(path), dest)
            try:
                legacy.rmdir()
            except OSError:
                pass

        legacy = INDEX_DIR / cat["folder"]
        if not legacy.is_dir():
            continue
        for path in legacy.iterdir():
            if not path.is_file():
                continue
            dest = target / path.name
            if dest.exists():
                path.unlink()
            else:
                shutil.move(str(path), dest)
        try:
            legacy.rmdir()
        except OSError:
            pass


def build() -> None:
    migrate_legacy_folders()
    nav_items = []
    sections = []

    for cat in CATEGORIES:
        nav_item, section = render_category(cat)
        nav_items.append(nav_item)
        sections.append(section)

    output = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DEXI — Codex de Conhecimentos</title>
  <meta name="description" content="Codex de conhecimentos intuitivos, linguísticos e científicos.">

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

  <style>
    /* Utilitários inspirados na paleta Tailwind (sem runtime JS) */
    .text-slate-700 {{ color: #334155; }}
    .text-slate-500 {{ color: #64748b; }}
    .text-sm {{ font-size: 0.875rem; }}
    :root {{
      --gold: #c9a227;
      --gold-light: #f5e6a8;
      --gold-glow: rgba(201, 162, 39, 0.25);
      --ink: #1e293b;
      --paper: #f8f7f4;
      --grid: rgba(148, 163, 184, 0.12);
    }}

    * {{ box-sizing: border-box; }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 10%, rgba(255, 255, 255, 0.9), transparent 40%),
        radial-gradient(circle at 80% 0%, var(--gold-glow), transparent 35%),
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px),
        var(--paper);
      background-size: auto, auto, 28px 28px, 28px 28px, auto;
      min-height: 100vh;
    }}

    .codex-shell {{
      display: grid;
      grid-template-columns: 280px 1fr;
      min-height: 100vh;
    }}

    @media (max-width: 991px) {{
      .codex-shell {{
        grid-template-columns: 1fr;
      }}
    }}

    .codex-sidebar {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      padding: 1.5rem 1.25rem;
      background: rgba(255, 255, 255, 0.82);
      backdrop-filter: blur(10px);
      border-right: 1px solid rgba(148, 163, 184, 0.25);
    }}

    @media (max-width: 991px) {{
      .codex-sidebar {{
        position: relative;
        height: auto;
        border-right: none;
        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
      }}
    }}

    .codex-brand {{
      text-align: center;
      margin-bottom: 1.5rem;
    }}

    .codex-brand img {{
      width: 88px;
      height: auto;
      filter: drop-shadow(0 8px 18px var(--gold-glow));
    }}

    .codex-brand h1 {{
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      margin: 0.75rem 0 0.15rem;
      color: #0f172a;
    }}

    .codex-brand p {{
      margin: 0;
      font-size: 0.72rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: #64748b;
    }}

    .codex-nav-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: #94a3b8;
      margin-bottom: 0.75rem;
    }}

    .codex-nav {{
      list-style: none;
      padding: 0;
      margin: 0 0 1.5rem;
    }}

    .codex-nav-category {{
      display: flex;
      gap: 0.75rem;
      align-items: flex-start;
      padding: 0.75rem;
      border-radius: 0.75rem;
      text-decoration: none;
      color: inherit;
      border: 1px solid transparent;
      margin-bottom: 0.5rem;
      transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
    }}

    .codex-nav-category:hover,
    .codex-nav-category:focus {{
      background: rgba(255, 255, 255, 0.9);
      border-color: rgba(201, 162, 39, 0.35);
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }}

    .codex-nav-category strong {{
      display: block;
      font-size: 0.95rem;
    }}

    .codex-nav-category small {{
      display: block;
      color: #64748b;
      font-size: 0.75rem;
    }}

    .codex-nav-icon {{
      font-size: 1.25rem;
      line-height: 1;
      color: var(--gold);
    }}

    .codex-nav-amber .codex-nav-icon {{ color: #d97706; }}
    .codex-nav-emerald .codex-nav-icon {{ color: #059669; }}
    .codex-nav-indigo .codex-nav-icon {{ color: #4f46e5; }}

    .codex-legend {{
      font-size: 0.78rem;
      color: #64748b;
      line-height: 1.5;
      padding: 0.875rem;
      border-radius: 0.75rem;
      background: rgba(248, 250, 252, 0.9);
      border: 1px dashed rgba(148, 163, 184, 0.35);
    }}

    .codex-main {{
      padding: 2rem clamp(1rem, 3vw, 3rem) 3rem;
      max-width: 980px;
    }}

    .codex-hero {{
      margin-bottom: 2.5rem;
      padding: 1.5rem 1.25rem;
      border-radius: 1rem;
      background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,250,235,0.85));
      border: 1px solid rgba(201, 162, 39, 0.2);
      box-shadow: 0 20px 50px rgba(15, 23, 42, 0.05);
    }}

    .codex-hero h2 {{
      font-size: clamp(1.4rem, 2.5vw, 2rem);
      font-weight: 700;
      margin-bottom: 0.5rem;
    }}

    .codex-hero p {{
      margin: 0;
      color: #475569;
      max-width: 60ch;
    }}

    .codex-section {{
      scroll-margin-top: 1.5rem;
      padding: 1.5rem;
      border-radius: 1rem;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(148, 163, 184, 0.2);
    }}

    .codex-section-amber {{ border-top: 4px solid #f59e0b; }}
    .codex-section-emerald {{ border-top: 4px solid #10b981; }}
    .codex-section-indigo {{ border-top: 4px solid #6366f1; }}

    .codex-section-header {{
      display: flex;
      gap: 1rem;
      align-items: center;
    }}

    .codex-section-icon {{
      font-size: 2rem;
      width: 3rem;
      height: 3rem;
      display: grid;
      place-items: center;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.9);
      box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.2);
    }}

    .codex-section-title {{
      font-size: 1.5rem;
      font-weight: 700;
      margin: 0;
    }}

    .codex-section-subtitle {{
      color: #64748b;
      font-size: 0.95rem;
    }}

    .codex-file-nav-label {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: #94a3b8;
      margin-bottom: 0.5rem;
    }}

    .codex-file-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .codex-nav-link {{
      display: inline-block;
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      color: #334155;
      text-decoration: none;
      font-size: 0.82rem;
    }}

    .codex-nav-link:hover,
    .codex-nav-link:focus {{
      border-color: var(--gold);
      color: #92400e;
      background: #fffbeb;
    }}

    .codex-details {{
      border: 1px solid #e2e8f0;
      border-radius: 0.875rem;
      background: #fff;
      overflow: hidden;
    }}

    .codex-summary {{
      list-style: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.875rem 1rem;
      background: #f8fafc;
      border-bottom: 1px solid transparent;
    }}

    .codex-details[open] .codex-summary {{
      border-bottom-color: #e2e8f0;
    }}

    .codex-summary::-webkit-details-marker {{
      display: none;
    }}

    .codex-summary::before {{
      content: "▸";
      color: var(--gold);
      transition: transform 0.2s;
    }}

    .codex-details[open] .codex-summary::before {{
      transform: rotate(90deg);
    }}

    .codex-entry-title {{
      font-weight: 600;
      word-break: break-word;
    }}

    .codex-badge {{
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      padding: 0.2rem 0.45rem;
      border-radius: 0.35rem;
      flex-shrink: 0;
    }}

    .codex-badge-image {{ background: #fef3c7; color: #92400e; }}
    .codex-badge-audio {{ background: #d1fae5; color: #065f46; }}
    .codex-badge-pdf {{ background: #fee2e2; color: #991b1b; }}
    .codex-badge-text {{ background: #e0e7ff; color: #3730a3; }}

    .codex-entry-body {{
      padding: 1rem;
    }}

    .codex-media img {{
      max-height: 70vh;
      object-fit: contain;
      width: 100%;
      background: #f8fafc;
    }}

    .codex-pdf {{
      width: 100%;
      min-height: 70vh;
      border: 1px solid #e2e8f0;
    }}

    .codex-text {{
      margin: 0;
      padding: 1rem;
      background: #0f172a;
      color: #e2e8f0;
      font-size: 0.88rem;
      line-height: 1.6;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid #1e293b;
    }}

    .codex-empty {{
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
    }}

    .link-gold {{
      color: #b45309;
    }}

    .codex-footer {{
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(148, 163, 184, 0.25);
      color: #94a3b8;
      font-size: 0.82rem;
    }}

    :target {{
      animation: codex-highlight 1.2s ease;
    }}

    @keyframes codex-highlight {{
      0% {{ box-shadow: 0 0 0 0 var(--gold-glow); }}
      40% {{ box-shadow: 0 0 0 8px var(--gold-glow); }}
      100% {{ box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <div class="codex-shell">
    <aside class="codex-sidebar">
      <div class="codex-brand">
        <img src="Dexi-Banner.png" alt="DEXI — Codex de Conhecimentos">
        <h1>DEXI</h1>
        <p>Codex de Conhecimentos</p>
      </div>

      <p class="codex-nav-label">Seções</p>
      <ul class="codex-nav">
        {"".join(nav_items)}
      </ul>

      <div class="codex-legend">
        <strong>Formatos suportados</strong><br>
        Imagens · Áudios · PDF · Texto<br><br>
        Coloque arquivos em <code>intuitios/</code>,
        <code>linguas/</code> e <code>scientias/</code> na raiz do projeto Dexi, depois execute
        <code>python build_codex.py</code>.
      </div>
    </aside>

    <main class="codex-main">
      <header class="codex-hero">
        <h2>Bem-vindo ao Codex</h2>
        <p>
          Visualize suas notas organizadas em três domínios do conhecimento —
          intuitivos, linguísticos e científicos — sem depender de JavaScript.
        </p>
      </header>

      {"".join(sections)}

      <footer class="codex-footer">
        DEXI Codex · Bootstrap 5 + utilitários Tailwind em CSS estático
      </footer>
    </main>
  </div>
</body>
</html>
"""

    (INDEX_DIR / "index.html").write_text(output, encoding="utf-8")
    print(f"Gerado: {INDEX_DIR / 'index.html'}")
    print(f"Pastas de conhecimento: {KNOWLEDGE_ROOT}")


if __name__ == "__main__":
    build()
