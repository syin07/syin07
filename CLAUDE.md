# GitHub profile README (syin07)

This repo is my GitHub profile page. `README.md` renders at github.com/syin07.

## Layout
- `README.md`: the profile. GitHub strips `<style>`, `<script>` and most attributes, so layout uses plain HTML tables, `align`, and `width`.
- `assets/banner.svg`: animated header. Generated, do not hand-edit: change `scripts/banner.py` and run `python3 scripts/banner.py assets/banner.svg`.
- `assets/activity.svg`: contribution waveform. Written daily by `.github/workflows/activity.yml` running `scripts/activity.py`. Never commit it by hand. Preview the design with `python3 scripts/activity.py --demo`, then delete the output before committing.

## Design rules
- Light background only. One accent colour, amber: `#F59E0B` for shapes (bars, cursor), `#D97706` for badge logos, and `#B45309` where the accent has to be read as small text. Body text `#1F2328` (GitHub's own), secondary text `#6B7280`, tracks `#E5E7EB`. No blue or purple.
- The banner sits on plain `#FFFFFF` with no frame or tint, so it blends into GitHub's light page and the row of link buttons under it reads as part of the same header. Its layout is centred on the vertical midline.
- Restrained: no typing-SVG services, trophy or stats cards, visitor counters, or rainbow badge walls.
- Every image is a self-contained SVG in this repo (CSS animation only, no external fonts or scripts). The only third-party images allowed are the shields.io tool badges.
- Animations must respect `prefers-reduced-motion` and look complete when frozen.
- Only list projects that have a public repo to link to. Don't invent results or metrics.

## Checking changes
- Open the SVG directly in a browser to watch the animation. To inspect one moment, pass a time in seconds as a second argument: `python3 scripts/banner.py /tmp/frame.svg 8.2`.
- GitHub serves SVGs through an image proxy and caches them for a few minutes; a hard refresh may be needed after pushing.
