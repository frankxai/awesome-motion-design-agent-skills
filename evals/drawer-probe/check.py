"""Run the interrupted-close source fixture in Chromium against its reference repair."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

REPAIR_JS = """
const pending = new WeakMap();
export function setDrawerOpen(panel, open) {
  clearTimeout(pending.get(panel));
  pending.delete(panel);
  panel.inert = !open;
  if (open) {
    panel.hidden = false;
    panel.classList.add('open');
  } else {
    panel.classList.remove('open');
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      panel.hidden = true;
    } else {
      pending.set(panel, setTimeout(() => {
        panel.hidden = true;
        pending.delete(panel);
      }, 300));
    }
  }
}
"""
REPAIR_CSS = """
@media (prefers-reduced-motion: reduce) {
  .drawer, .drawer.open { transition: none; transform: none; }
}
"""
VERSION = 'web-motion-auditor/interrupted-close-v1'
SOURCE_HASH = '79d304de799b3eaf88e502ada767ccfdb9b84538560a1be350e98a47b41cf26c'


def run(browser, css, js, preference):
    page = browser.new_page(reduced_motion=preference)
    try:
        page.clock.install()
        page.set_content('<aside class="drawer" id="a" hidden><button>A</button></aside>'
                         '<aside class="drawer" id="b" hidden><button>B</button></aside>')
        page.add_style_tag(content=css)
        # Load the fixture as an ES module so the original source bytes are executed.
        page.evaluate("""async source => {
          const url = URL.createObjectURL(new Blob([source], {type:'text/javascript'}));
          const {setDrawerOpen} = await import(url);
          URL.revokeObjectURL(url);
          window.toggle = (id, open) => setDrawerOpen(document.getElementById(id), open);
        }""", js)
        page.evaluate("toggle('a',true); toggle('b',true)")
        duration = page.locator('#a').evaluate('a => getComputedStyle(a).transitionDuration')
        page.evaluate("toggle('a',false); toggle('b',false)")
        immediate = page.locator('#a').evaluate('a => a.hidden || a.inert')
        page.clock.run_for(50)
        page.evaluate("toggle('a',true)")
        page.clock.run_for(301)
        return {
            'transitionDuration': duration,
            'reopenedPanelVisible': page.locator('#a').is_visible(),
            'otherPanelClosed': page.locator('#b').is_hidden(),
            'closingPanelInertOrHiddenImmediately': immediate,
        }
    finally:
        page.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--chromium', default=shutil.which('chromium'))
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    fixture = json.loads(raw)
    if digest != SOURCE_HASH or fixture['id'] != VERSION:
        raise ValueError('Pass the pinned upstream fixture. See README.')
    files = fixture['input']['files']
    js, css = files['drawer.js'], files['drawer.css']
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium, headless=True)
        results = {}
        for condition, (script, style) in {
            'upstream': (js, css), 'referenceRepair': (REPAIR_JS, css + REPAIR_CSS),
        }.items():
            results[condition] = {pref: run(browser, style, script, pref)
                                  for pref in ('no-preference', 'reduce')}
        version = browser.version
        browser.close()
    report = {'fixture': VERSION, 'sourceSha256': digest, 'chromium': version,
              'playwright': importlib.metadata.version('playwright'), 'observations': results}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    for condition, probes in results.items():
        repaired = condition == 'referenceRepair'
        for pref, observation in probes.items():
            expected = {
                'transitionDuration': '0s' if repaired and pref == 'reduce' else '0.3s',
                'reopenedPanelVisible': repaired, 'otherPanelClosed': True,
                'closingPanelInertOrHiddenImmediately': repaired,
            }
            if observation != expected:
                raise SystemExit(f'{condition}/{pref}: {observation} != {expected}')


if __name__ == '__main__':
    main()
