"""Run with python3 tests/languages.py while the site is served on port 8001.
Requires Python Playwright and /usr/bin/chromium.
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    context = browser.new_context()
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:8001/', wait_until='networkidle')
    english = page.locator('main').text_content()
    assert page.locator('html').get_attribute('lang') == 'en'
    page.select_option('#site-language', 'el')
    assert page.locator('html').get_attribute('lang') == 'el'
    assert page.title() == 'LotNexus — Κάθε λειτουργία. Συνδεδεμένη.'
    assert 'Κάθε λειτουργία.' in page.locator('h1').inner_text()
    assert page.locator('meta[name="description"]').get_attribute('content').startswith('Γνωρίστε')
    assert page.locator('nav').first.get_attribute('aria-label') == 'Κύρια πλοήγηση'
    # Every alphabetic body text is translated or is an intentional brand/code.
    untranslated = page.evaluate('''() => {
      const allowed = new Set(['English','Ελληνικά','Lot','Nexus','ERP + MES','Android PDA','Starter','Professional','Enterprise','FG-024','RM-108','FG-025']);
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      const missing = [];
      while(walker.nextNode()) {
        const n = walker.currentNode, s = n.textContent.trim();
        if (!n.parentElement.closest('script,style') && /[a-z]/i.test(s) && !/[α-ωά-ώ]/i.test(s) && !allowed.has(s)) missing.push(s);
      }
      return missing;
    }''')
    assert not untranslated, untranslated
    page.reload(wait_until='networkidle')
    assert page.locator('html').get_attribute('lang') == 'el'
    page.locator('.docs-side a[href="#guide-installation"]').click()
    assert page.locator('#guide-installation').evaluate('(el) => el.open')
    for width in [320,390,768,1024,1280]:
        page.set_viewport_size({'width': width, 'height': 900})
        assert page.locator('#site-language').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
    page.set_viewport_size({'width':390,'height':844})
    page.locator('.nav-toggle').click()
    assert page.locator('.nav-toggle').get_attribute('aria-label') == 'Κλείσιμο πλοήγησης'
    page.select_option('#site-language','en')
    assert page.locator('.nav-toggle').get_attribute('aria-label') == 'Close navigation'
    page.keyboard.press('Escape')
    assert page.locator('.nav-toggle').get_attribute('aria-expanded') == 'false'
    assert page.locator('main').text_content() == english
    page.reload(wait_until='networkidle')
    assert page.locator('html').get_attribute('lang') == 'en'
    # Storage denial must not break switching.
    isolated = browser.new_context()
    isolated.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new Error('blocked')}})")
    fallback = isolated.new_page()
    fallback.goto('http://127.0.0.1:8001/')
    fallback.select_option('#site-language','el')
    assert fallback.locator('html').get_attribute('lang') == 'el'
    no_js = browser.new_context(java_script_enabled=False).new_page()
    no_js.goto('http://127.0.0.1:8001/')
    assert no_js.locator('h1').is_visible()
    assert not no_js.locator('#site-language').is_visible()
    assert not errors, errors
    browser.close()
    print('PASS: translations, metadata, accessibility labels, persistence, round trip, mobile menu, five viewport widths, blocked storage, no-JS fallback')
