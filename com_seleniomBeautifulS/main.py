#!/usr/bin/env python3
"""
Scraper for comunica.pje.jus.br consulta pages using curl_cffi (impersonate chrome110).
Saves results to results.json

Dependencies:
    pip install curl-cffi beautifulsoup4
"""

import json
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from curl_cffi import requests

# Base URL you provided
BASE_URL = "https://comunica.pje.jus.br/consulta?texto=distribu%C3%ADdo&dataDisponibilizacaoInicio=2025-11-01&dataDisponibilizacaoFim=2025-11-10"

# impersonation (chrome110)
IMPERSONATE = "chrome110"

# polite delay between requests (seconds)
DELAY = 0.6

session = requests.Session(impersonate=IMPERSONATE, verify=True, timeout=30)

def get_soup(url, save_html=False):
    resp = session.get(url)
    resp.raise_for_status()
    html = resp.text
    
    # Debug: save HTML to file
    if save_html:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[DEBUG] HTML salvo em debug_page.html ({len(html)} bytes)")
    
    return BeautifulSoup(html, "html.parser"), resp

def extract_card_data(article):
    """
    Extract data from a single <article class="card"> element.
    Returns dict.
    """
    import re
    data = {}

    # Process number - try find span.numero-unico-formatado or text "Processo"
    proc_span = article.select_one(".numero-unico-formatado")
    if proc_span and proc_span.get_text(strip=True):
        data["processo"] = proc_span.get_text(strip=True).replace("Processo", "").strip()
    else:
        # fallback: look for "Processo " in text
        txt = article.get_text(separator=" ", strip=True)
        if "Processo" in txt:
            m = re.search(r"Processo\s+([0-9\-\.]+)", txt)
            data["processo"] = m.group(1).strip() if m else txt[:80]

    # Extract print/certidao link from header
    print_link = article.select_one('a[href*="certidao"]')
    if print_link:
        data["link_certidao"] = print_link.get("href")

    # Sidebar summary (aside.card-sumary)
    aside = article.select_one("aside.card-sumary")
    if aside:
        # iterate info-sumary blocks to extract labeled fields
        for info in aside.select(".info"):
            info_sumary = info.select_one(".info-sumary")
            if not info_sumary:
                continue
                
            b = info_sumary.find("b")
            if b:
                key_text = b.get_text(strip=True).rstrip(":").lower()
                # Make a copy to extract text
                info_copy = BeautifulSoup(str(info_sumary), "html.parser")
                b_copy = info_copy.find("b")
                if b_copy:
                    b_copy.extract()
                value = info_copy.get_text(" ", strip=True)
                
                # Handle special cases
                if key_text == "inteiro teor":
                    link = info_sumary.find("a")
                    if link and link.get("href"):
                        data["link_inteiro_teor"] = link.get("href")
                elif key_text not in ["parte(s)", "advogado(s)"]:
                    data[key_text] = value

        # Extract partes (parties) - polo ativo/passivo
        partes = []
        for parte_block in aside.select(".info-sumary"):
            tooltip = parte_block.select_one(".tooltip-polo")
            if tooltip:
                # Get the tooltip text (Polo Ativo/Passivo)
                tooltip_span = tooltip.select_one(".tooltip-text")
                polo_tipo = tooltip_span.get_text(strip=True) if tooltip_span else ""
                
                # Get the party name (text after the tooltip div)
                # Remove the tooltip element to get clean text
                parte_copy = BeautifulSoup(str(parte_block), "html.parser")
                tooltip_copy = parte_copy.select_one(".tooltip-polo")
                if tooltip_copy:
                    tooltip_copy.extract()
                nome = parte_copy.get_text(strip=True)
                
                if nome and polo_tipo:
                    partes.append({
                        "polo": polo_tipo,
                        "nome": nome
                    })
        if partes:
            data["partes"] = partes

        # Extract advogados (lawyers)
        advogados = []
        in_advogado_section = False
        for info in aside.select(".info"):
            info_text = info.get_text(strip=True)
            if "Advogado(s)" in info_text:
                in_advogado_section = True
                continue
            
            if in_advogado_section:
                # Check if this block has OAB info
                if "OAB" in info_text:
                    # Extract clean lawyer info
                    info_sumary = info.select_one(".info-sumary")
                    if info_sumary:
                        # Remove icon if present
                        icon = info_sumary.select_one("mat-icon")
                        if icon:
                            icon.extract()
                        lawyer_text = info_sumary.get_text(" ", strip=True)
                        if lawyer_text:
                            advogados.append(lawyer_text)
                elif info_text and not info.select_one("b"):
                    # Might be continuation of lawyer info
                    pass
                else:
                    # End of advogado section
                    break
        
        if advogados:
            data["advogados"] = advogados

    # Main panel distribution text (section.content-texto .tab_panel2 or similar)
    panel = article.select_one("section.content-texto .tab_panel2")
    if panel:
        data["texto_distribuicao"] = panel.get_text(" ", strip=True)
    else:
        # fallback: search for strings like "distribuido para"
        content = article.select_one("section.content-texto")
        if content:
            t = content.get_text(" ", strip=True)
            if "distribu" in t.lower():
                data["texto_distribuicao"] = t[:500]

    return data

def find_pagination_links(soup, base_url):
    """
    Find numeric pagination links and return a sorted list of absolute URLs (unique).
    Looks for buttons, links, and clickable elements with numeric text.
    """
    links = set()
    page_numbers = set()
    
    # 1) Look for pagination containers (nav, ul, div with pagination-related classes)
    candidates = soup.find_all(lambda tag: tag.name in ("nav","ul","div","mat-paginator") and 
                               (tag.get("class") and any("pagin" in c.lower() or "page" in c.lower() for c in " ".join(tag.get("class")))) or
                               (tag.get("id") and any("pagin" in tag.get("id").lower() or "page" in tag.get("id").lower())))
    
    for cand in candidates:
        # Look for <a>, <button>, or clickable elements with numeric text
        for elem in cand.find_all(["a", "button", "span", "div"]):
            txt = elem.get_text(strip=True)
            if txt.isdigit():
                page_num = int(txt)
                page_numbers.add(page_num)
                
                # Try to get href if it's a link
                href = elem.get("href")
                if href:
                    links.add(urljoin(base_url, href))
    
    # 2) Global search for <a> or <button> with numeric text
    if not links:
        for elem in soup.find_all(["a", "button"]):
            txt = elem.get_text(strip=True)
            if txt.isdigit():
                page_num = int(txt)
                page_numbers.add(page_num)
                
                href = elem.get("href")
                if href:
                    links.add(urljoin(base_url, href))
    
    # 3) If we found page numbers but no links, construct URLs with page parameter
    if page_numbers and not links:
        print(f"[*] Found page numbers but no direct links: {sorted(page_numbers)}")
        print(f"[*] Will construct URLs with page parameter")
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        for page_num in sorted(page_numbers):
            parsed = urlparse(base_url)
            qs = parse_qs(parsed.query)
            qs["page"] = [str(page_num)]
            new_query = urlencode({k: v[0] for k, v in qs.items()})
            new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
            links.add(new_url)
    
    # Sort by page number
    def page_key(u):
        try:
            parsed = urlparse(u)
            qs = parse_qs(parsed.query)
            for k in ("page","pagina","p","pg"):
                if k in qs:
                    try:
                        return int(qs[k][0])
                    except:
                        pass
            # fallback: take last path segment numeric
            seg = parsed.path.rstrip("/").split("/")[-1]
            return int(seg) if seg.isdigit() else 0
        except:
            return 0
    
    return sorted(links, key=page_key)

def collect_all_pages(base_url):
    """
    Main logic:
    1) fetch base_url
    2) detect numeric page links and iterate them (including base page)
    3) if no links found, fallback to incrementing ?page=N until no results
    """
    print(f"[+] Fetching base URL: {base_url}")
    soup, resp = get_soup(base_url, save_html=True)  # Debug: save HTML
    all_results = []

    # extract from first page
    articles = soup.select("article.card")
    print(f"  - articles on page 1: {len(articles)}")
    for a in articles:
        all_results.append(extract_card_data(a))

    # find pagination links (hrefs)
    page_links = find_pagination_links(soup, base_url)
    page_urls = []

    if page_links:
        # include unique absolute URLs and make sure base is included
        page_urls = [u for u in page_links]
        # ensure base_url is first if not present
        if base_url not in page_urls:
            page_urls.insert(0, base_url)
        # dedupe while preserving order
        seen = set()
        page_urls_unique = []
        for u in page_urls:
            if u not in seen:
                seen.add(u)
                page_urls_unique.append(u)
        page_urls = page_urls_unique
        # remove the first one because we already processed base (unless it's different)
        if page_urls and page_urls[0] == base_url:
            page_urls = page_urls[1:]
        print(f"[+] Detected {len(page_urls)+1} pages (including page 1).")
    else:
        # fallback: try page param incremental
        print("[!] No pagination links detected by href. Falling back to incremental page param approach.")
        page_urls = []
        max_empty_streak = 2
        page = 2
        empty_streak = 0
        while True:
            # try adding ?page=N preserving existing query params
            parsed = urlparse(base_url)
            qs = parse_qs(parsed.query)
            qs["page"] = [str(page)]
            new_query = urlencode({k: v[0] for k, v in qs.items()})
            new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
            print(f"  -> Trying page {page}: {new_url}")
            s, r = get_soup(new_url)
            arts = s.select("article.card")
            if not arts:
                empty_streak += 1
                if empty_streak >= max_empty_streak:
                    print(f"  -> no more articles after page {page}. Stopping.")
                    break
                else:
                    page += 1
                    time.sleep(DELAY)
                    continue
            # got articles
            for a in arts:
                all_results.append(extract_card_data(a))
            page += 1
            time.sleep(DELAY)
        # done fallback
        return all_results

    # If we have explicit page URLs, iterate them
    for idx, p_url in enumerate(page_urls, start=2):
        try:
            print(f"[+] Fetching page {idx}: {p_url}")
            s, r = get_soup(p_url)
            arts = s.select("article.card")
            print(f"  - found {len(arts)} articles")
            if not arts:
                # maybe this page is empty, continue
                continue
            for a in arts:
                all_results.append(extract_card_data(a))
            time.sleep(DELAY)
        except Exception as e:
            print(f"[!] Error fetching page {p_url}: {e}")

    return all_results

def main():
    results = collect_all_pages(BASE_URL)
    print(f"[+] Total records collected: {len(results)}")
    # Save to results.json
    out_file = "results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved results to {out_file}")

if __name__ == "__main__":
    main()
