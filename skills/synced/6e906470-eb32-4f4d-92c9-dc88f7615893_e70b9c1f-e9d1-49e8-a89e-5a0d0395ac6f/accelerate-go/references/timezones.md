# Timezone handling

The user's local IANA timezone (from preflight locale, stored in `holidays.md`) is the only day boundary
that matters. (Adapted from O33.)

| System | Returns times as | Handle |
|---|---|---|
| M365 calendar | In the tz you pass / the item's tz | Compare against local day bounds |
| M365 mail | UTC | Filter in UTC (convert local bounds → UTC), attribute in local |
| M365 chats | UTC | Same as mail |
| GO (`timeslot_dayview`, `timeslot_upsert`) | Plain ISO date, no time | The **local** day the activity happened |

Convert with `zoneinfo` (Python) so DST is handled — never hard-code offsets.

```python
from datetime import datetime
from zoneinfo import ZoneInfo
local = ZoneInfo(user_iana)                     # e.g. "Australia/Sydney"
start = datetime(y, m, d, 0, 0, tzinfo=local)
end   = datetime(y, m, d + 1, 0, 0, tzinfo=local)
utc_start = start.astimezone(ZoneInfo("UTC")).isoformat()
utc_end   = end.astimezone(ZoneInfo("UTC")).isoformat()
```

Common mistakes: filtering mail with a local day boundary marked `Z`; attributing a UTC timestamp to the
wrong local day; hard-coded offsets that break on DST. AUS zones differ by city
(`Australia/Sydney`, `Australia/Melbourne`, `Australia/Brisbane`, `Australia/Adelaide`,
`Australia/Perth`, `Australia/Hobart`); NZ is `Pacific/Auckland` (Chatham `Pacific/Chatham`).

Note: `zoneinfo`/Python runs on Desktop + local Code, **not** claude.ai web.
