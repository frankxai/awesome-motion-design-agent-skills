Audit the motion and animation behavior of every HTML file in `fixtures/`.

Look for problems a user would hit with reduced motion enabled, on touch devices, with a keyboard, when interactions are interrupted or repeated, when content is mounted and unmounted, and in scroll and animation performance. Some files may have no problems.

Reply with only a JSON object that matches `findings.schema.json`:

```json
{
  "findings": [
    {"fixture": "01-example.html", "line": 12, "category": "performance", "severity": "high", "summary": "One sentence.", "fix": "One sentence."}
  ]
}
```

`category` is one of: reduced-motion, performance, interruption, cleanup, touch, keyboard. Report each distinct problem once, at the line where the fix belongs. Do not report problems you have not found in the code.
