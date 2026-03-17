#!/usr/bin/env python3
"""
Convert week HTML files from horizontal slide-deck to vertically scrollable single-page format.
"""

import re, os

# ── Common CSS that replaces the slide/presentation-container CSS ──
SCROLL_CSS = """
        /* ====================== SCROLL PAGE BASE ====================== */
        *, *::before, *::after { box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            overflow-y: auto;
            background: #0D1B2A;
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            color: #E2E8F0;
        }

        /* ── Page wrapper ── */
        #page-wrapper {
            width: 100%;
        }

        /* ── Each "slide" becomes a stacked section ── */
        .slide {
            width: 100%;
            min-height: 100vh;
            position: relative;
            display: flex;
            flex-direction: column;
            padding: 4rem 5% 3rem 5%;
            box-sizing: border-box;
            overflow: visible;
        }

        /* ── Slide header stays at top, never shrinks ── */
        .slide-header {
            flex-shrink: 0;
            position: relative;
            z-index: 2;
        }

        /* ── Content area is no longer scrollable — flows naturally ── */
        .content-area {
            flex: 1;
            min-height: 0;
            overflow: visible;
            padding-right: 0;
            margin-top: 0.5rem;
            position: relative;
            z-index: 2;
        }

        /* Remove old scrollbar styles — not needed for content-area */
        .content-area::-webkit-scrollbar { display: none; }

        /* ── Divider between slides ── */
        .slide + .slide {
            border-top: 2px solid rgba(0, 112, 173, 0.18);
        }

        /* ====================== SLIDE THEMES ====================== */
        .slide-dark {
            background: linear-gradient(135deg, #0D1B2A 0%, #0F2847 100%);
            color: #E2E8F0;
        }
        .slide-dark::before {
            content: '';
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 20% 50%, rgba(0,112,173,0.12) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(18,171,219,0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        .slide-dark .slide-header,
        .slide-dark .content-area,
        .slide-dark .max-w-5xl { position: relative; z-index: 1; }

        .slide-light {
            background: linear-gradient(135deg, #F4F6F9 0%, #EEF2F8 100%);
            color: #1E293B;
        }
        .slide-light::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 20% 50%, rgba(0,112,173,0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .slide-white {
            background: #FFFFFF;
            color: #1E293B;
        }
        .slide-white::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 80% 20%, rgba(0,112,173,0.03) 0%, transparent 60%);
            pointer-events: none;
            z-index: 0;
        }

        /* ====================== PATTERNS ====================== */
        .bg-dots {
            background-image: radial-gradient(circle, rgba(0,112,173,0.06) 1px, transparent 1px);
            background-size: 28px 28px;
        }
        .bg-grid {
            background-image:
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 44px 44px;
        }
        .bg-grid-light {
            background-image:
                linear-gradient(rgba(0,112,173,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,112,173,0.04) 1px, transparent 1px);
            background-size: 44px 44px;
        }

        /* ====================== TYPOGRAPHY ====================== */
        h1 {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            line-height: 1.1;
            margin: 0 0 0.75rem 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        h2 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            line-height: 1.2;
            margin: 0 0 0.5rem 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin: 0 0 0.3rem 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        p {
            line-height: 1.7;
            margin: 0 0 0.75rem 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        /* ====================== COMPONENTS ====================== */
        .accent-line { height: 4px; width: 80px; background: linear-gradient(90deg,#0070AD,#12ABDB); border-radius: 2px; }

        .outcome-card {
            background: rgba(0,112,173,0.06);
            border: 1px solid rgba(0,112,173,0.15);
            border-left: 4px solid #0070AD;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 8px rgba(0,112,173,0.08);
            transition: all 0.3s ease;
        }
        .outcome-card:hover {
            background: rgba(0,112,173,0.1);
            border-color: rgba(0,112,173,0.25);
            box-shadow: 0 8px 24px rgba(0,112,173,0.2);
            transform: translateX(4px);
        }
        .slide-light .outcome-card, .slide-white .outcome-card {
            background: #FFFFFF;
            border: 1px solid #E2E7EE;
            border-left: 4px solid #0070AD;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        .slide-light .outcome-card:hover, .slide-white .outcome-card:hover {
            box-shadow: 0 12px 28px rgba(0,0,0,0.12);
            border-color: #0070AD;
            background: #F8FAFC;
        }

        .section-label { font-size: 0.7rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 0.35rem; }
        .slide-dark .section-label { color: #7DD3E8; }
        .slide-light .section-label, .slide-white .section-label { color: #0070AD; }

        .badge-in {
            background: rgba(18,171,219,0.12);
            color: #12ABDB;
            border: 1px solid rgba(18,171,219,0.3);
            padding: 0.15rem 0.65rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 700;
            display: inline-block;
        }
        .badge-out {
            background: rgba(0,179,136,0.1);
            color: #00B388;
            border: 1px solid rgba(0,179,136,0.25);
            padding: 0.15rem 0.65rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 700;
            display: inline-block;
        }
        .badge-day {
            background: linear-gradient(135deg, #0070AD, #12ABDB);
            color: #fff;
            padding: 0.2rem 0.75rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(0,112,173,0.2);
        }
        .badge-phase {
            background: rgba(0,112,173,0.1);
            color: #0070AD;
            border: 1px solid rgba(0,112,173,0.2);
            padding: 0.15rem 0.65rem;
            border-radius: 999px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }

        .check-item { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem; }
        .check-icon { color: #00B388; font-weight: bold; flex-shrink: 0; margin-top: 2px; }

        /* ====================== CODE BLOCKS ====================== */
        pre {
            background: #0D1B2A;
            padding: 1rem 1.1rem;
            border-radius: 8px;
            font-family: 'Fira Code', monospace;
            font-size: 0.72rem;
            overflow-x: auto;
            overflow-y: visible;
            border: 1px solid #1B2D45;
            color: #CBD5E1;
            line-height: 1.6;
            margin: 0.5rem 0;
            position: relative;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
            word-wrap: break-word;
            white-space: pre-wrap;
            user-select: text;
            -webkit-user-select: text;
            cursor: text;
        }
        pre:hover {
            border-color: #0070AD;
            box-shadow: 0 6px 24px rgba(0,112,173,0.2);
        }
        .slide-light pre, .slide-white pre {
            background: #1B2D45;
            border-color: #243B5A;
            color: #E2E8F0;
        }
        pre::-webkit-scrollbar { height: 5px; }
        pre::-webkit-scrollbar-track { background: rgba(0,0,0,0.15); border-radius: 3px; }
        pre::-webkit-scrollbar-thumb { background: rgba(0,112,173,0.5); border-radius: 3px; }
        pre::-webkit-scrollbar-thumb:hover { background: rgba(0,112,173,0.8); }

        .code-copy-btn {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: #0070AD;
            border: 1px solid #12ABDB;
            color: white;
            padding: 0.3rem 0.7rem;
            border-radius: 4px;
            font-size: 0.65rem;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            cursor: pointer;
            opacity: 0;
            transition: all 0.2s ease;
            z-index: 10;
        }
        pre:hover .code-copy-btn { opacity: 1; }
        .code-copy-btn:hover { background: #12ABDB; color: #0D1B2A; }
        .code-copy-btn.copied { background: #00B388; border-color: #00B388; opacity: 1; }

        .scqa-box {
            border-radius: 12px;
            padding: 1.15rem 1.4rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .scqa-box:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,112,173,0.25);
        }

        /* ====================== LISTS ====================== */
        .sl ul { list-style: none; padding-left: 0; }
        .sl ul li {
            font-size: 0.82rem; line-height: 1.6; margin-bottom: 0.45rem;
            padding-left: 1.3rem; position: relative;
        }
        .sl ul li::before { content: '▸'; position: absolute; left: 0; color: #12ABDB; font-weight: bold; }
        .slide-dark .sl ul li { color: #CBD5E1; }
        .slide-light .sl ul li, .slide-white .sl ul li { color: #334155; }

        .sl ol {
            list-style: none;
            padding-left: 0;
            counter-reset: activity-counter;
        }
        .sl ol li {
            font-size: 0.82rem; line-height: 1.6; margin-bottom: 0.55rem;
            padding-left: 2rem; position: relative;
            counter-increment: activity-counter;
        }
        .sl ol li::before {
            content: counter(activity-counter);
            position: absolute;
            left: 0;
            top: 0.05rem;
            width: 1.35rem; height: 1.35rem;
            background: linear-gradient(135deg, #0070AD, #12ABDB);
            color: #fff;
            font-size: 0.65rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
            line-height: 1;
        }
        .slide-dark .sl ol li { color: #CBD5E1; }
        .slide-light .sl ol li, .slide-white .sl ol li { color: #1E293B; }

        /* ====================== INLINE CODE ====================== */
        :not(pre) > code {
            font-family: 'Fira Code', monospace;
            font-size: 0.78em;
            padding: 0.1em 0.38em;
            border-radius: 4px;
            background: #0D1B2A;
            color: #12ABDB;
            border: 1px solid rgba(18,171,219,0.25);
            word-break: break-word;
        }
        .slide-light :not(pre) > code,
        .slide-white :not(pre) > code {
            background: #EEF4FB;
            color: #005A8C;
            border: 1px solid rgba(0,112,173,0.2);
        }

        /* ====================== LIGHT/WHITE SLIDE TEXT ====================== */
        .slide-light p, .slide-white p { color: #1E293B; }
        .slide-light h2, .slide-white h2 { color: #0D1B2A; }
        .slide-light h3, .slide-white h3 { color: #0D1B2A; }
        .slide-light .outcome-card .check-item span,
        .slide-white .outcome-card .check-item span { color: #1E293B; }
        .slide-light .outcome-card .check-item strong,
        .slide-white .outcome-card .check-item strong { color: #003D5C; }
        .slide-light .text-sm, .slide-white .text-sm { color: #1E293B; }
        .slide-light .text-sm strong, .slide-white .text-sm strong { color: #003D5C; }
        .slide-light a, .slide-white a { color: #0070AD; }
        .slide-light .check-icon, .slide-white .check-icon { color: #00875A; }
        .slide-light .section-label, .slide-white .section-label { color: #005A8C; font-weight: 700; }

        /* ====================== OVERFLOW / WRAPPING ====================== */
        .content-area .grid, .content-area .grid > * { min-width: 0; }
        .content-area { word-wrap: break-word; overflow-wrap: break-word; }
        .content-area pre { max-width: 100%; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }

        /* ====================== TOP BAR ====================== */
        .cg-topbar {
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, #0070AD 0%, #12ABDB 50%, #00B388 100%);
            z-index: 10;
        }

        /* Day circle */
        .day-circle {
            width: 56px; height: 56px; border-radius: 50%;
            background: linear-gradient(135deg, #0070AD, #12ABDB);
            display: flex; align-items: center; justify-content: center;
            color: white; font-family: 'Outfit'; font-weight: 800; font-size: 0.85rem;
            flex-shrink: 0;
            box-shadow: 0 6px 20px rgba(0,112,173,0.3);
            min-width: 56px;
        }

        /* ====================== WEEK NAV BAR ====================== */
        #week-nav {
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(13,27,42,0.97);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(0,112,173,0.25);
            padding: 0.5rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }

        /* ── "Back to top" floating button ── */
        #back-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0070AD, #12ABDB);
            color: white;
            border: none;
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(0,112,173,0.4);
            z-index: 500;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
        }
        #back-to-top.visible { opacity: 1; transform: translateY(0); }
        #back-to-top:hover { background: linear-gradient(135deg, #12ABDB, #00B388); box-shadow: 0 6px 24px rgba(0,112,173,0.5); }

        /* ── Slide "anchor" heading for the section nav ── */
        .slide-anchor {
            display: block;
            position: relative;
            top: -80px;
            visibility: hidden;
            pointer-events: none;
        }

        /* ====================== RESPONSIVE ====================== */
        @media (max-width: 768px) {
            .slide { padding: 3.5rem 4% 2.5rem 4%; }
            .grid.grid-cols-2 { grid-template-columns: 1fr !important; }
            .grid.grid-cols-3 { grid-template-columns: 1fr !important; }
            pre { font-size: 0.68rem; }
        }

        /* ====================== PRINT / PDF ====================== */
        @media print {
            @page { size: A4 portrait; margin: 1.5cm; }
            body { overflow: visible !important; background: white !important; color: #1E293B !important; }
            #week-nav, #back-to-top, .no-print { display: none !important; }
            .slide {
                padding: 1.5rem 1.5rem 1rem 1.5rem !important;
                page-break-after: always !important;
                break-inside: avoid !important;
                min-height: 0 !important;
                overflow: visible !important;
            }
            .slide::before { display: none !important; }
            .slide-dark { background-color: #0D1B2A !important; color: #E2E8F0 !important; }
            .slide-light { background-color: #F4F6F9 !important; color: #1E293B !important; }
            .slide-white { background-color: #FFFFFF !important; color: #1E293B !important; }
            .slide-dark h2, .slide-dark h3, .slide-dark p { color: #E2E8F0 !important; }
            .slide-light h2, .slide-light h3, .slide-light p { color: #1E293B !important; }
            pre { overflow: visible !important; max-width: 100% !important; font-size: 0.6rem !important; white-space: pre-wrap !important; break-inside: avoid !important; box-shadow: none !important; }
            .code-copy-btn { display: none !important; }
            * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; animation: none !important; transition: none !important; }
        }
"""

# ── Minimal JS (copy buttons + back-to-top; NO slide nav) ──
SCROLL_JS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    // ── Code copy buttons ──
    document.querySelectorAll('pre').forEach((pre, idx) => {
        if (getComputedStyle(pre).position === 'static') pre.style.position = 'relative';
        const btn = document.createElement('button');
        btn.className = 'code-copy-btn';
        btn.textContent = 'COPY';
        btn.type = 'button';
        pre.insertBefore(btn, pre.firstChild);
        btn.addEventListener('click', async (e) => {
            e.preventDefault(); e.stopPropagation();
            const code = pre.querySelector('code');
            const text = (code ? code.innerText : pre.innerText) || '';
            if (!text) return;
            try {
                await navigator.clipboard.writeText(text);
                btn.textContent = '✓ COPIED'; btn.classList.add('copied');
            } catch {
                const ta = document.createElement('textarea');
                ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
                document.body.appendChild(ta); ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                btn.textContent = '✓ COPIED'; btn.classList.add('copied');
            }
            setTimeout(() => { btn.textContent = 'COPY'; btn.classList.remove('copied'); }, 2500);
        });
    });

    // ── Auto-wrap slide headers (elements before .content-area) ──
    document.querySelectorAll('.slide').forEach(slide => {
        const ca = slide.querySelector('.content-area');
        if (!ca) return;
        const nodes = [];
        let node = slide.firstElementChild;
        while (node && node !== ca) { nodes.push(node); node = node.nextElementSibling; }
        if (nodes.length > 0) {
            const wrapper = document.createElement('div');
            wrapper.className = 'slide-header';
            slide.insertBefore(wrapper, nodes[0]);
            nodes.forEach(n => wrapper.appendChild(n));
        }
    });

    // ── Back-to-top button ──
    const btn = document.getElementById('back-to-top');
    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 400);
    });
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
});
</script>
"""

# ── Back-to-top button HTML ──
BACK_TO_TOP = '\n<button id="back-to-top" title="Back to top" aria-label="Back to top">↑</button>\n'

def transform_file(src_path, dst_path):
    with open(src_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # ── 1. Replace <style> block entirely ──
    # Find the first <style> and its closing </style>
    style_start = html.index('<style>')
    style_end   = html.index('</style>', style_start) + len('</style>')
    html = html[:style_start] + '<style>' + SCROLL_CSS + '    </style>' + html[style_end:]

    # ── 2. Remove Anime.js script tag ──
    html = re.sub(r'\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/animejs/[^"]+"></script>', '', html)

    # ── 3. Replace body open: remove overflow:hidden ──
    # body tag stays the same (no inline style on it in these files)

    # ── 4. Replace #presentation-container with #page-wrapper ──
    html = html.replace('<div id="presentation-container">', '<div id="page-wrapper">')

    # ── 5. Remove the inline <style> that sets padding-top on #presentation-container ──
    html = re.sub(r'<style>#presentation-container\s*\{[^}]+\}\s*\.slide\s*\{[^}]+\}\s*</style>', '', html)

    # ── 6. Make #week-nav sticky (already handled in CSS; remove old fixed inline style) ──
    # The week-nav div has inline style with position:fixed — replace with position:sticky via id
    html = re.sub(
        r'(<div id="week-nav")[^>]*(>)',
        r'<div id="week-nav">',
        html
    )

    # ── 7. Remove navigation overlays div (left/right click zones) ──
    html = re.sub(
        r'<!--\s*NAVIGATION OVERLAYS.*?-->\s*<div class="absolute inset-0.*?</div>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    # Also remove individually if comment pattern differs
    html = re.sub(
        r'<div class="absolute inset-0 w-full h-full z-40 flex no-print pointer-events-none">.*?</div>',
        '',
        html,
        flags=re.DOTALL
    )

    # ── 8. Remove slide indicator and counter divs ──
    html = re.sub(r'<div id="slide-indicator"[^>]*></div>', '', html)
    html = re.sub(r'<div id="slide-counter"[^>]*></div>', '', html)

    # ── 9. Remove old JavaScript block (everything between <!-- JAVASCRIPT --> and </script>) ──
    # Remove the big <script> block at the bottom
    html = re.sub(
        r'<!--\s*=+\s*-->\s*<!--\s*JAVASCRIPT\s*.*?-->\s*<!--\s*=+\s*-->\s*<script>.*?</script>',
        '',
        html,
        flags=re.DOTALL
    )
    # Also handle files without the comment
    html = re.sub(
        r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\'.*?</script>',
        '',
        html,
        flags=re.DOTALL
    )

    # ── 10. Add back-to-top button + new JS before </body> ──
    html = html.replace('</body>', BACK_TO_TOP + SCROLL_JS + '\n</body>')

    # ── 11. Clean up end of #page-wrapper — remove leftover whitespace ──
    html = html.replace('</div><!-- end presentation-container -->', '</div><!-- end page-wrapper -->')

    # ── 12. Write output ──
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓  {os.path.basename(src_path)} → {os.path.basename(dst_path)}")

if __name__ == '__main__':
    base = '/Users/sreeni/Documents/Code/Java-Training-Material'
    for week_file in ['week1.html', 'week2.html', 'week3.html', 'week4.html', 'week5.html', 'week6.html']:
        src = os.path.join(base, week_file)
        transform_file(src, src)
    print("\nAll done!")
