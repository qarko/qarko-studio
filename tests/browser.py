import functools
import http.server
import json
import os
import re
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'test-results'
OUT.mkdir(exist_ok=True)
WIDTHS = [320, 375, 390, 430, 768, 1024, 1440, 1920]
SITES = ['agency-landing', 'saas-showcase']
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
report = {'matrix': [], 'interactions': [], 'stress': [], 'no_js': [], 'browsers': {}}

def layout(page, label):
    result = page.evaluate('''() => {
      const root = document.documentElement;
      const clipped = [...document.querySelectorAll('h1,h2,h3,p,label,summary,.button')].filter(el => {
        if (!el.checkVisibility() || el.closest('[aria-hidden="true"], [role="img"]')) return false;
        const css=getComputedStyle(el);
        return el.scrollWidth > el.clientWidth + 2 && css.display !== 'inline';
      }).map(el => el.tagName + '.' + el.className);
      return {width: innerWidth, scrollWidth: root.scrollWidth, clipped};
    }''')
    assert result['scrollWidth'] <= result['width'] + 1, (label, result)
    assert not result['clipped'], (label, result)
    assert page.locator('img').evaluate_all('(images) => images.every(image => image.complete && image.naturalWidth > 0)'), label + ' images'
    assert page.locator('h1').count() == 1
    return result

def local_form(page, form):
    form.locator('[data-submit]').click()
    expect(form.locator('[data-error]')).to_contain_text('필수 항목')
    form.locator('[name="email"]').fill('invalid')
    form.locator('[name="team"]').fill('예시 팀')
    form.locator('[name="goal"]').fill('반복 요청을 정리하는 흐름을 검토합니다.')
    form.locator('[data-submit]').click()
    assert not form.evaluate('(form) => form.checkValidity()')
    form.locator('[name="email"]').fill('team@example.com')
    form.locator('[data-submit]').click()
    expect(form.locator('[role="status"]')).to_contain_text('전송하거나 저장하지 않습니다')

with sync_playwright() as p:
    for engine in ['chromium', 'webkit']:
        browser = getattr(p, engine).launch()
        report['browsers'][engine] = browser.version
        for protocol in ['file', 'http']:
            for site in SITES:
                for width in WIDTHS:
                    context = browser.new_context(viewport={'width':width,'height':900}, has_touch=width < 768)
                    external=[]
                    def route(request_route):
                        url=request_route.request.url
                        if url.startswith('http') and not url.startswith(f'http://127.0.0.1:{server.server_port}/'):
                            external.append(url);request_route.abort()
                        else: request_route.continue_()
                    context.route('**/*', route)
                    if protocol == 'file' and engine == 'chromium': context.set_offline(True)
                    page=context.new_page(); errors=[]
                    page.on('pageerror',lambda error: errors.append(str(error)))
                    url=(ROOT/site/'index.html').as_uri() if protocol=='file' else f'http://127.0.0.1:{server.server_port}/{site}/index.html'
                    page.goto(url);page.evaluate('document.fonts.ready');
                    label=f'{engine}/{protocol}/{site}/{width}'
                    result=layout(page,label)
                    assert not errors,(label,errors)
                    assert not external,(label,'external requests')
                    assert page.evaluate('document.fonts.check("400 16px Pretendard")'), label+' font'
                    assert page.locator('a[href="#"]').count()==0
                    if width in [375,768,1440] and protocol=='file':
                        page.screenshot(path=str(OUT/f'{engine}-{site}-{width}.png'),full_page=True)
                    if width==375:
                        opener=page.locator('[data-open-inquiry]:visible').first
                        opener.focus();page.keyboard.press('Enter')
                        expect(page.locator('dialog')).to_be_visible()
                        expect(page.locator('dialog h2')).to_be_focused()
                        for key,count in [('Tab',15),('Shift+Tab',8)]:
                            for _ in range(count):
                                page.keyboard.press(key)
                                assert page.evaluate('document.querySelector("dialog").contains(document.activeElement)'),label+' focus trap'
                        local_form(page,page.locator('dialog form'))
                        page.keyboard.press('Escape')
                        expect(page.locator('dialog')).not_to_be_visible();expect(opener).to_be_focused()
                        opener.click();page.locator('[data-close]').click();expect(opener).to_be_focused()
                        expect(page.locator('body')).not_to_have_class(re.compile(r'.*modal-open.*'))
                        assert page.evaluate('getComputedStyle(document.body).overflow')!='hidden'
                        if site=='agency-landing':
                            page.locator('.mobile-dock a').tap()
                            assert page.evaluate('location.hash')=='#work'
                            page.locator('.site-footer').scroll_into_view_if_needed()
                            page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)')
                            assert page.locator('.site-footer').bounding_box()['y']+page.locator('.site-footer').bounding_box()['height'] <= page.locator('.mobile-dock').bounding_box()['y']+1
                            for target in page.locator('.mobile-dock a,.mobile-dock button').all():
                                box=target.bounding_box(); assert box['width']>=44 and box['height']>=44
                        else:
                            for key,value in [('launch','대시보드'),('feedback','내보내기'),('meeting','온보딩')]:
                                page.locator('#sample-select').select_option(key);page.locator('#organize').tap();expect(page.locator('.output-summary')).to_contain_text(value)
                            tabs=page.locator('[role="tab"]')
                            tabs.nth(0).focus()
                            for key,index in [('ArrowRight',1),('ArrowLeft',0),('End',2),('Home',0),('ArrowDown',1),('ArrowUp',0)]:
                                page.keyboard.press(key);expect(tabs.nth(index)).to_be_focused();expect(tabs.nth(index)).to_have_attribute('aria-selected','true')
                                expect(page.locator('[role="tabpanel"]:visible')).to_have_count(1)
                            for tab in tabs.all():tab.tap();expect(tab).to_have_attribute('aria-selected','true')
                            for detail in page.locator('details').all():
                                detail.locator('summary').tap();expect(detail).to_have_attribute('open','');detail.locator('summary').tap();assert detail.get_attribute('open') is None
                            for plan in ['starter','team','business']:
                                page.locator(f'[data-plan="{plan}"]').tap();expect(page.locator('#contact-plan')).to_have_value(plan)
                            local_form(page,page.locator('#contact form'))
                            if protocol=='http':assert page.evaluate('localStorage.length + sessionStorage.length')==0
                        report['interactions'].append(label)
                    report['matrix'].append({'case':label,**result})
                    context.close()
        for site in SITES:
            context=browser.new_context(viewport={'width':320,'height':900},reduced_motion='reduce')
            page=context.new_page();page.goto((ROOT/site/'index.html').as_uri());page.evaluate('document.fonts.ready')
            page.add_style_tag(content='html{font-size:200%}')
            layout(page,f'{engine}/{site}/200%-text')
            page.locator('[data-open-inquiry]:visible').first.click();
            assert page.locator('dialog').evaluate('(dialog) => getComputedStyle(dialog).animationName')=='none'
            assert page.locator('dialog').evaluate('(dialog) => dialog.scrollHeight > dialog.clientHeight')
            page.locator('[data-close]').click()
            report['stress'].append(f'{engine}/{site}/320/200%-text/reduced-motion');context.close()
            context=browser.new_context(java_script_enabled=False,viewport={'width':375,'height':900})
            page=context.new_page();page.goto((ROOT/site/'index.html').as_uri())
            expect(page.locator('noscript')).to_be_visible();expect(page.locator('h1')).to_be_visible()
            for submit in page.locator('[data-submit]').all():expect(submit).to_be_disabled()
            if site=='saas-showcase':
                assert page.locator('[data-panel]:visible').count()==3
                page.locator('details summary').first.click();expect(page.locator('details').first).to_have_attribute('open','')
            layout(page,f'{engine}/{site}/no-js')
            report['no_js'].append(f'{engine}/{site}');context.close()
        browser.close()
server.shutdown()
(OUT/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'browsers':report['browsers'],'matrix_passes':len(report['matrix']),'interaction_suites':len(report['interactions']),'stress_suites':len(report['stress']),'no_js_suites':len(report['no_js'])},ensure_ascii=False))
