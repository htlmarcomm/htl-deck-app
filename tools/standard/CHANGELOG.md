# Slide Standard — changelog (Oct 2026)

Applied: "Slide Standard: Implementation Brief". Each slide keeps its own design; spacing, type and alignment were standardised.

## What was added
- **Design tokens** (`:root`, in `<style id="slide-standard">` of `src/frontend/app.html`; sources in `tools/standard/*.css`). Covers margins (54/54/54/48 pt), the 12-column grid, type sizes and line heights, the spacing steps and the logo height. The canvas is 1280 × 720 px, so 1 pt = 4/3 px.
- **Type scale:** Heading (Raleway 50 pt, caps), Sub-heading (26 pt), Body (20 pt), Detail (14 pt), all in TT Norms. One addition to the brief: **Caption, 9 pt**, for dense card text (project cards, org chart, captions). Without it those slides would have to be redesigned.
- **Footer** on every slide: page number on the left, HTL logo on the right, both in the bottom margin.
- **Raleway** is loaded from Google Fonts, with fallbacks.

## Slides changed
| Slides | What was fixed |
|---|---|
| All 28 project slides (BFSI, CRE, DC, Education, Hospitality, Restaurants, Industrial, Manufacturing, Residential, High Rise, South ×5, Pune ×3, MEP ×2, VRV, New Wins) | Rebuilt in one layout (the "Major MEP Projects" style). Photo panel with the title, red-ruled label, and cards with photo / name / location / rule / AREA–SCOPE lines. Cards sit edge to edge in the safe area, with text in the Caption style. The dark caption gradient was removed from 83 photos (new files; the originals are kept). |
| About Us, Journey, Our Expertise, Why HTL, Quality Policy, Safety, Service Implementation, Driving Innovation, Dashboard & Reporting, Key Clients, Key Repeat Clients | Heading moved to the 54/54 pt corner in Raleway 50 pt, keeping its bold/light words. Text snapped to the four styles. Content moved inside the safe area; centred paragraphs left-aligned. |
| Org Structure | Laid out by hand: seven equal person columns, names and titles centred under each photo, no overlaps. |
| Sectors We Deliver Across | Fixed two-row layout, so it no longer re-flows and runs off the slide in small previews. The cards fill the slide. |
| Client Testimonials | The letters are as large as the slide width allows and centred in the space under the heading. |
| Commissioning to Asset Mgmt, Innovation in Designing | Heading at the standard corner and font; size kept smaller (see below). |
| Capability deck, 18 content screens | In deck-slide view only (the interactive proposal is unchanged): heading in Raleway 50 pt at 54/54 pt, text snapped to the styles, footer added. Small kicker labels that collided with the heading were moved above it. |
| Add-slide templates (blank, table, text from your files) | New slides start on the grid. Heading text box at 54/54 pt; body boxes 5 columns wide under the heading; tables full width; standard type styles; footer. |

## Slides that do not fully fit the standard (for review)
1. **Covers kept as designed:** Title Page, Thank You, and the Capability title, intro and section dividers (About HTL, About the Project, 03, 04, 05). Their large title is a design element, not a slide heading.
2. **Headings smaller than 50 pt**, because 50 pt does not fit the space:
   - The 28 project slides: the title is in the photo panel at 23 pt; at 50 pt one word is wider than the panel.
   - The two Major Projects photo-panel slides (customisable, Hospital).
   - Commissioning to Asset Mgmt (23 pt) and Innovation in Designing (26 pt): headings in a narrow column.
   - Capability: HNI (39 pt), Hinduja Group (45 pt), Project Understanding (42 pt) and Project Organization (39 pt).
3. **Heading not at the corner:** Capability "Who We Are", where the heading sits in the right column beside the map (moving it would swap the layout). Vision/Mission/Values and Planning–ERP have no single heading.
4. **Text past the safe area:**
   - About Us (the stats row sits in the bottom margin).
   - Vision/Mission/Values (the full-bleed coloured panels).
   - Major Projects customisable and Hospital (the card text sits in the right margin).
   - Why HTL for MEP (the right-hand labels).
   - Capability: Agenda, New Wins, Hinduja Group, Capital Items and Site Report run 2–29 pt into the bottom margin. Most content screens run up to 37 pt into the right margin, because their layouts are wider than the safe area.
5. **Very small print kept** (under 6.5 pt, inside logos, tables and org boxes): Capability Hinduja Group, Capital Items, Org Chart, Site Report, Project Understanding, HNI and LEED. Enlarging it breaks the boxes it sits in.
6. **Grid:** Org Structure uses 7 equal columns, because 7 people per row does not divide the 12-column grid.
7. **Not converted:** Capability "House Planning Schedule" and "Procurement Tracker" are placeholder slides with no design yet.

Old decks keep the slide designs they were saved with. Use **Replace slide** to bring a slide up to the new standard.
