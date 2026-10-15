# -*- coding: utf-8 -*-
"""Project slides: cards are spread over the fewest rows (max 4 a row) as evenly as possible
(6 -> 3 + 3, 5 -> 3 + 2, 7 -> 4 + 3) and every row stretches edge to edge. A 12-column grid
(12 = lcm of 1..4) lets rows of 1-4 cards line up; each card spans 12 / (cards in its row)."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "src", "frontend", "app.html")
s = open(p, encoding="utf-8").read()


def sw(o, n):
    global s
    assert s.count(o) == 1, (s.count(o), o[:100])
    s = s.replace(o, n)


def row_counts(n):
    r = -(-n // 4)
    base, extra = divmod(n, r)
    return [base + 1 if i < extra else base for i in range(r)]


# snippets: span + end-of-row class on every card
a = s.find('id="all-snippets-data"')
o = s.find(">", a) + 1
e = s.find("</script>", o)
orig = s[o:e]
data = json.loads(orig)
done = 0
for k, v in data.items():
    if 'class="bp-slide"' not in v:
        continue
    n = len(re.findall(r'<article class="bp-card', v))
    spans = []
    eor = []
    for c in row_counts(n):
        for j in range(c):
            spans.append(12 // c)
            eor.append(j == c - 1)
    it = iter(zip(spans, eor))

    def fix(m):
        sp, last = next(it)
        return '<article class="bp-card%s" style="grid-column:span %d">' % (" bp-eor" if last else "", sp)

    v2 = re.sub(r'<article class="bp-card(?: bp-eor)?"(?: style="[^"]*")?>', fix, v)
    data[k] = v2.replace('data-rows="%d"' % -(-n // 4), 'data-rows="%d"' % -(-n // 4))
    done += 1
compact = '": "' not in orig[:400]
out = json.dumps(data, ensure_ascii=False, separators=(",", ":") if compact else None).replace("</script", "<\\/script")
s = s[:o] + out + s[e:]

# CSS
sw("display:grid; grid-template-columns:repeat(4,183px); column-gap:40px;", "display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); column-gap:40px;")
sw('.bp-grid[data-rows="1"]{grid-template-rows:252px;}', '.bp-grid[data-rows="1"]{grid-template-rows:290px;}')

# live layout (editor: add / remove cards)
sw("""    var cards = realCards(grid), n = cards.length;
    grid.setAttribute('data-rows', Math.max(1, Math.min(3, Math.ceil(n / 4))));
    cards.forEach(function(c, i){ c.classList.toggle('bp-eor', i % 4 === 3 || i === n - 1); });
  }""", """    var cards = realCards(grid), n = cards.length;
    var rows = Math.max(1, Math.min(3, Math.ceil(n / 4)));
    grid.setAttribute('data-rows', rows);
    // spread the cards over the rows as evenly as possible (6 -> 3 + 3, 7 -> 4 + 3); each row fills the width
    var base = Math.floor(n / rows), extra = n % rows, i = 0;
    for(var r = 0; r < rows; r++){
      var k = base + (r < extra ? 1 : 0);
      for(var j = 0; j < k && i < n; j++, i++){
        cards[i].style.gridColumn = 'span ' + (12 / k);
        cards[i].classList.toggle('bp-eor', j === k - 1);
      }
    }
  }""")
sw("  // BFSI-design grid: 4 cards a row, 1-3 rows; the last card of each row ends its divider line",
   "  // BFSI-design grid: up to 4 cards a row, 1-3 rows, rows stretch edge to edge; the last card of each row ends its divider line")

open(p, "w", encoding="utf-8").write(s)
print("ok", done, "slides")
