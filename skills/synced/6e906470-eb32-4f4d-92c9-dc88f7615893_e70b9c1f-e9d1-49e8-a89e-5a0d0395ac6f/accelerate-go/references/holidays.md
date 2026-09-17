# Public holidays

Don't propose entries on a public holiday in the user's locale unless they say they worked. (Adapted from
O33; **AUS default** for AT, NZ supported.)

## Two levels

- **National** — e.g. Australia Day, ANZAC Day, Christmas.
- **Regional** — state/territory (AUS) or anniversary region (NZ), e.g. Melbourne Cup Day (VIC),
  Auckland Anniversary (NZ).

## Three independent concepts — don't conflate

- **Country** (`Australia`) — drives national holidays.
- **Region** (`NSW` / `VIC` / … or an NZ anniversary region) — drives regional holidays. Ask; don't infer
  from city alone.
- **IANA timezone** (`Australia/Sydney`) — day boundaries. AUS differs by city; NZ mainland is
  `Pacific/Auckland`.

## AUS states / NZ regions

AUS: NSW, VIC, QLD, SA, WA, TAS, ACT, NT. NZ anniversary regions: Auckland, Wellington, Canterbury, Otago,
Southland, Taranaki, Hawke's Bay, Marlborough, Nelson, West Coast, Chatham Islands.

## `holidays.md` cache structure (in the preferences folder)

```
## Locale
Country: Australia
Region:  NSW
IANA tz: Australia/Sydney

## 2026 holidays observed
- 2026-01-01 (Thu) - New Year's Day
- 2026-01-26 (Mon) - Australia Day
- 2026-04-03 (Fri) - Good Friday
- 2026-04-25 (Sat) - ANZAC Day
- 2026-12-25 (Fri) - Christmas Day
- 2026-12-28 (Mon) - Boxing Day observed
... (populate the user's state list)
```

TODO: fill the per-state AUS 2026 list. On a holiday, skip drafting and note it in the run report; if the
user says they worked, run the normal draft → confirm → submit. Refresh yearly.
