/* Shared numerical model and drawing used by the interactive and the two film adapters. */
(function (scope) {
  const studies = [
    {
      name: "Linear",
      formula: "p(t) = t",
      note: "Equal intervals cover equal distances.",
      ease: (t) => t,
    },
    {
      name: "Ease out",
      formula: "p(t) = 1 − (1 − t)³",
      note: "Cover distance early. Settle gently.",
      ease: (t) => 1 - (1 - t) ** 3,
    },
    {
      name: "Ease in–out",
      formula: "p(t) = 3t² − 2t³",
      note: "Accelerate, cross, then settle.",
      ease: (t) => t * t * (3 - 2 * t),
    },
  ];
  const blue = "#2544bb",
    ink = "#1c253a",
    white = "#f4f1e8",
    hot = "#ff916c";
  const sans = "Arial, Helvetica, sans-serif",
    mono = "monospace";
  const round = (value) => Number(value.toFixed(2));
  function pathFor(ease, band) {
    const points = [];
    for (let i = 0; i <= 80; i++) {
      const t = i / 80;
      const envelope = Math.sin(Math.PI * t);
      points.push(
        (i === 0 ? "M" : "L") +
          round(50 + t * 510 + band * 0.32 * envelope) +
          " " +
          round(310 - 224 * ease(t) + band * envelope),
      );
    }
    return points.join(" ");
  }
  function geometry(index) {
    const ease = studies[index].ease;
    let grid = "",
      lines = "",
      samples = "";
    for (let i = 0; i <= 10; i++) {
      const x = 50 + i * 51;
      grid += '<path d="M' + x + ' 58V328" stroke-dasharray="2 8"/>';
    }
    for (let i = 0; i <= 4; i++) {
      const y = 310 - i * 56;
      grid += '<path d="M40 ' + y + 'H570" stroke-dasharray="2 8"/>';
    }
    for (let i = 0; i < 23; i++) {
      const band = 1.6 + 2.15 * i;
      lines +=
        '<path d="' +
        pathFor(ease, band) +
        '" fill="none" stroke="#d0dcff" stroke-opacity="' +
        round(0.76 - i * 0.019) +
        '" stroke-width="1.15"/>';
    }
    for (let i = 0; i <= 10; i++) {
      const t = i / 10;
      samples +=
        '<circle cx="' +
        (50 + 510 * t) +
        '" cy="' +
        round(310 - 224 * ease(t)) +
        '" r="2.9" fill="' +
        white +
        '"/>';
    }
    return (
      '<g fill="none" stroke="#b9ceff" stroke-opacity=".39">' +
      grid +
      "</g>" +
      lines +
      '<path d="' +
      pathFor(ease, 0) +
      '" fill="none" stroke="' +
      white +
      '" stroke-width="2.3"/>' +
      samples +
      '<g class="plot-labels" font-family="' +
      mono +
      '" font-size="13" fill="#d4ddff"><text x="49" y="352">0.0 s</text><text x="560" y="352" text-anchor="end">1.0 s</text><text x="47" y="36">POSITION / TIME</text></g>'
    );
  }
  const plots = studies.map((_, index) => geometry(index));
  function marker(index, t) {
    const x = round(50 + 510 * t),
      y = round(310 - 224 * studies[index].ease(t));
    return (
      '<path d="M' +
      x +
      " " +
      y +
      'V317" stroke="' +
      hot +
      '" stroke-dasharray="3 5"/><circle cx="' +
      x +
      '" cy="' +
      y +
      '" r="8.5" fill="' +
      hot +
      '" stroke="' +
      ink +
      '" stroke-width="2"/>'
    );
  }
  function chart(index, t) {
    return (
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 610 379" aria-hidden="true">' +
      plots[index] +
      "<g data-cursor>" +
      marker(index, t) +
      "</g></svg>"
    );
  }
  function text(x, y, size, content, options = {}) {
    return (
      '<text x="' +
      x +
      '" y="' +
      y +
      '" font-family="' +
      (options.font || sans) +
      '" font-size="' +
      size +
      '" fill="' +
      (options.fill || ink) +
      '" ' +
      (options.attrs || "") +
      ">" +
      content +
      "</text>"
    );
  }
  // Three three-second plates. A fixed hold brackets the one-second demonstration.
  function filmFrame(seconds, width, height) {
    const index = Math.max(0, Math.min(2, Math.floor(seconds / 3)));
    const t = Math.max(0, Math.min(1, seconds - index * 3 - 0.72));
    const item = studies[index],
      portrait = height > width;
    const w = portrait ? 720 : 1280,
      h = portrait ? 1280 : 720;
    const pad = portrait ? 50 : 68,
      plateX = portrait ? 34 : 574,
      plateY = portrait ? 471 : 137;
    const plateW = portrait ? 652 : 654,
      plateH = portrait ? 453 : 433;
    const graphic =
      '<g transform="translate(' +
      plateX +
      " " +
      plateY +
      ')"><rect width="' +
      plateW +
      '" height="' +
      plateH +
      '" fill="' +
      blue +
      '"/><g transform="translate(0 10) scale(' +
      round(plateW / 610) +
      ')">' +
      plots[index] +
      marker(index, t) +
      "</g></g>";
    let paper =
      '<rect width="' +
      w +
      '" height="' +
      h +
      '" fill="' +
      white +
      '"/><path d="M' +
      pad +
      " 98H" +
      (w - pad) +
      '" stroke="' +
      ink +
      '"/>';
    paper +=
      text(pad, 74, 19, "MOTION STUDIES", { font: mono }) +
      text(w - pad, 74, 19, "TIME / POSITION", {
        font: mono,
        attrs: 'text-anchor="end"',
      });
    const lineTop = portrait ? 191 : 198;
    paper += text(pad, lineTop, 21, "Easing, plotted.", { font: mono });
    const words =
      index === 2
        ? ["Ease", "in–out"]
        : index === 1
          ? ["Ease", "out"]
          : ["Linear"];
    words.forEach((word, i) => {
      paper += text(pad, lineTop + 103 + i * 91, portrait ? 105 : 96, word, {
        attrs: 'letter-spacing="-6" font-weight="600"',
      });
    });
    const position = portrait ? 1013 : 505;
    paper +=
      graphic +
      text(pad, position, portrait ? 34 : 25, item.note) +
      text(pad, position + 50, portrait ? 25 : 21, item.formula, {
        font: mono,
      });
    // Each plate uses the same clock and moving mass so distance can be compared.
    const y = portrait ? 1162 : 627,
      end = w - pad,
      travel = end - pad;
    paper +=
      '<path d="M' +
      pad +
      " " +
      y +
      "H" +
      end +
      '" stroke="' +
      ink +
      '" stroke-width="2"/>';
    for (let i = 0; i <= 10; i++)
      paper +=
        '<path d="M' +
        (pad + (travel * i) / 10) +
        " " +
        (y - 6) +
        'v12" stroke="' +
        ink +
        '"/>';
    const x = round(pad + travel * item.ease(t));
    paper +=
      '<circle cx="' +
      x +
      '" cy="' +
      y +
      '" r="12" fill="' +
      hot +
      '" stroke="' +
      ink +
      '" stroke-width="2"/>';
    paper +=
      text(pad, y + 45, 18, "DISTANCE", { font: mono }) +
      text(end, y + 45, 18, "1 SECOND", {
        font: mono,
        attrs: 'text-anchor="end"',
      });
    return (
      '<svg xmlns="http://www.w3.org/2000/svg" width="' +
      width +
      '" height="' +
      height +
      '" viewBox="0 0 ' +
      w +
      " " +
      h +
      '">' +
      paper +
      "</svg>"
    );
  }
  scope.MotionStudy = { studies, chart, marker, filmFrame };
})(globalThis);
