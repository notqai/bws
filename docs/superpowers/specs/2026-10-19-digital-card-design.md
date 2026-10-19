# Digital business card: Mazinah Binti Mohd Masri

Date: 2026-10-19

## Goal

Replace the physical name card with a shareable digital one. The client (BWS Engineering Sdn Bhd) says people sometimes forget to carry cards, so Mazinah should be able to hand over her details from her phone at any time. First card is for Mazinah only; the structure must let more staff cards be added later without redesign.

## Constraints

- BWS site is a static site in this repo (`site/`, served by Vercel, no build step). The card is a page inside it.
- `www.bwsengineeringsb.com` still points to the old Wix site and Qai has no access to it. The card is live at `bwsengsdnbhd.vercel.app/card/mazinah` until the domain is switched over, then at `www.bwsengineeringsb.com/card/mazinah` with no code change.
- English UI. The Jawi company name appears only as a logo element. No photo, BM toggle, NFC or analytics in v1.

## Files

| Path | Purpose |
|---|---|
| `site/card/mazinah.html` | The card page (mobile-first, `noindex`, no site header or footer) |
| `site/card/mazinah.vcf` | Static vCard 3.0 served for the Save Contact button |
| `site/card/mazinah-qr.svg` | QR code of the live URL (see QR section) |
| `site/assets/css/card.css` | Card-only styles; imports nothing, uses the `:root` tokens from `styles.css` loaded first |
| `tools/make_card.py` | Optional: generates the `.vcf` and QR from one data block, so a new staff card is a data change |

Reused, not copied: `styles.css` tokens, self-hosted Source Serif 4 / Source Sans 3 fonts, `logo.svg`, `logo-white.svg`, Noto Naskh Arabic styling for the Jawi name.

## Page content (top to bottom)

1. **Header:** `logo-white.svg` on `--ink`, Jawi name beneath.
2. **Identity:** "Mazinah Binti Mohd Masri", "Executive Director / Personnel & Administration Manager", BWS Engineering Sdn Bhd.
3. **Primary action:** large **Save Contact** button linking to `mazinah.vcf` (`download` attribute).
4. **Quick actions:** Call (`tel:+60198894946`), WhatsApp (`https://wa.me/60198894946`), Email (`mailto:mazinahmasribws@gmail.com`), Website (`https://www.bwsengineeringsb.com`).
5. **Offices** (two cards):
   - Miri: Lot 1743, Block 3 MCLD, Piasau Industrial Estate Phase III, Jalan Prunus 1, 98000 Miri, Sarawak. Tel 085-652743 / 44 / 45, Fax 085-652709, bwsesb@gmail.com, bws@bwsengineeringsb.com. Maps: `https://www.google.com/maps?cid=4214669276461699859`.
   - Bintulu: Lot 782, Block 20, Kemena Land District, Jalan Tanjung Kidurong, 97007 Bintulu, Sarawak. Tel 086-252476. Maps: `https://www.google.com/maps?cid=6044021619715074034`.
6. **Credentials strip:** ISO 9001 (TÜV NORD, Cert No. 44 100 072059), ISO 45001 (BSI, OHS 796482), Registration No. 200201029529 (597192-V). CIDB G7 and PETRONAS/PETROS licence badges are shown only if the client confirms (they are already on the main site's top bar).
7. **Share:** `navigator.share()` button where supported, copy-link fallback; plus the QR code for scanning from another phone.

## vCard fields

`FN`/`N`: Mazinah Binti Mohd Masri; `ORG`: BWS Engineering Sdn Bhd; `TITLE`: Executive Director / Personnel & Administration Manager; `TEL;CELL`: +60198894946; `TEL;WORK`: +6085652743; `EMAIL`: mazinahmasribws@gmail.com; `URL`: company website; `ADR;WORK`: Miri office. Line endings CRLF, UTF-8.

## QR code

The QR encodes the card URL and a printed QR cannot be changed. Until the domain is switched over the QR points to the `vercel.app` link and is marked temporary in the README. Regenerate it with `tools/make_card.py` after cutover and do not print it before then.

## Behaviour and quality

- `<meta name="robots" content="noindex">`, and the card is excluded from `sitemap.xml`, so her mobile number does not appear in search.
- Mobile-first, single column, touch targets of at least 44px, AA contrast using existing tokens (white on `--brand-blue` and `--ink` only; `--brand-sky` never carries white text).
- Works with JavaScript disabled except the Share button, which is hidden without it.

## Testing

- Browser check at 375px and desktop width.
- `.vcf` imports correctly on iPhone and Android (name, title, both numbers, email, address).
- All `tel:`, WhatsApp, `mailto:` and Maps links resolve.
- QR scans back to the intended URL.
- Page absent from `sitemap.xml`, `noindex` present.

## Open items

- Confirm with the client whether to show CIDB G7 and PETRONAS/PETROS licence on the card.
- Confirm Mazinah's WhatsApp is the same number as her mobile (019-889 4946).
- Regenerate the QR code after the domain cutover.
