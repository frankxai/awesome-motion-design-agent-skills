# Interrupted drawer close

On 19 November 2026, Chromium 153.0.8010.0 executed the original PR #42 fixture and a small reference repair under normal and reduced motion. The probe opens two panels, requests two closes, reopens only the first after 50 ms, and advances the browser clock past the original close deadline.

| Observation | Original | Reference repair |
| --- | --- | --- |
| Reopened first panel still visible after stale timer | No | Yes |
| Independently closing second panel hidden | Yes | Yes |
| Closing panel immediately hidden or inert | No | Yes |
| Computed transition duration under reduced motion | 300 ms | 0 ms |

The reference repair tracks each panel's timer, cancels superseded work, immediately makes closing content inert and honors the motion preference. These are fixture-level observations. The test does not invoke the motion auditor, grade a model, measure FPS or establish focus return to the application's trigger.

Run manually with Python, Playwright 1.62.0 and Chromium. The fixture is pinned to the contributing PR and checked before its two source files run.

```sh
git fetch origin refs/pull/42/head
git show 3f8e637803abfbca790a82ece57a561c1795a72f:evals/outcomes/web-motion-auditor/interrupted-close.json > /tmp/interrupted-close.json
python evals/drawer-probe/check.py /tmp/interrupted-close.json --output /tmp/drawer-observations.json
```

Supply `--chromium /path/to/executable` for an alternate local browser. A mismatch exits nonzero and retains the observations. The published receipt is [observations.json](observations.json).
