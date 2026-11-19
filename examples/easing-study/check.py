"""Exercise the local demo in Chromium, save screenshots, and print observed timings."""

import argparse
import json
from pathlib import Path
from statistics import median

from playwright.sync_api import sync_playwright

SOURCE = Path(__file__).resolve().parent


def check(args):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((SOURCE / "index.html").as_uri())
        page.screenshot(path=args.output / "easing-desktop.png")
        page.keyboard.press("Tab")
        assert page.locator("input:checked").evaluate("el=>el===document.activeElement")
        page.keyboard.press("ArrowRight")
        assert page.locator("#curve-name").inner_text() == "Ease in–out"
        page.keyboard.press("Tab")
        assert page.locator("button").evaluate("el=>el===document.activeElement")
        # Measure frame-callback intervals during the animation, including main-thread contention.
        intervals = page.evaluate("""async () => {
          const times = [];
          document.getElementById('play').click();
          return await new Promise(resolve => {
            function sample(now) {
              times.push(now);
              if (now - times[0] >= 1050) resolve(times.slice(1).map((t,i)=>t-times[i]));
              else requestAnimationFrame(sample);
            }
            requestAnimationFrame(sample);
          });
        }""")
        assert page.locator("[data-cursor] circle").get_attribute("cx") == "560"
        page.locator("button").click()
        page.get_by_text("Linear", exact=True).first.click()
        page.wait_for_timeout(1100)
        assert page.locator("#curve-name").inner_text() == "Linear"
        assert page.locator("[data-cursor] circle").get_attribute("cx") == "560"
        page.locator("button").focus()
        page.emulate_media(reduced_motion="reduce")
        page.wait_for_function(
            "document.activeElement===document.querySelector('input:checked')"
        )
        assert page.locator("button").is_hidden()
        assert page.locator("#equation").inner_text() == "p(t) = t"
        phone = browser.new_context(
            viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
        )
        mobile = phone.new_page()
        mobile.goto((SOURCE / "index.html").as_uri())
        mobile.get_by_text("Ease in–out", exact=True).first.tap()
        mobile.locator("button").tap()
        mobile.wait_for_timeout(1100)
        assert mobile.locator("#curve-name").inner_text() == "Ease in–out"
        assert mobile.locator("[data-cursor] circle").get_attribute("cx") == "560"
        assert mobile.evaluate("document.documentElement.scrollWidth <= innerWidth")
        mobile.screenshot(path=args.output / "easing-mobile.png", full_page=True)
        offline = browser.new_context(java_script_enabled=False)
        fallback = offline.new_page()
        fallback.goto((SOURCE / "index.html").as_uri())
        assert fallback.locator("noscript p").is_visible()
        assert fallback.locator("#plot svg").is_visible()
        assert not errors, errors
        print(
            json.dumps(
                {
                    "browser": browser.version,
                    "checks": [
                        "desktop",
                        "keyboard",
                        "interruption",
                        "live reduced motion",
                        "touch emulation",
                        "mobile width",
                        "JavaScript off",
                    ],
                    "desktop_raf_intervals": len(intervals),
                    "median_interval_ms": round(median(intervals), 2),
                    "max_interval_ms": round(max(intervals), 2),
                },
                indent=2,
            )
        )
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", help="Installed Chromium executable")
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    options.output.mkdir(parents=True, exist_ok=True)
    check(options)
