# ⑤ Favourites

Saved timeslot templates that speed the daily loop. Verified against Live 2026-08-11.

## Read

- `favourite_list()` — enabled favourites (+ a count of disabled). `includeDisabled: true` shows all,
  including closed-project ones.
- Favourites also surface inside `timeslot_dayview(includeFavourites: true)` — offer matching favourites
  before searching projects when logging time.
- Each favourite carries `favouriteID` + `projectID` in the metadata line.

## Manage — `favourite_manage` (Destructive — always confirm)

`action` = `add` | `update` | `enable` | `disable` | `remove`.

- **add**: `projectID` (from `project_search`) + optional `defaultDetails` (default description) + `udefs`.
- **update**: single `favouriteID` + the fields to change.
- **enable / disable / remove**: `favouriteID` as a single int or JSON array, e.g. `[101, 102, 103]`.

```
favourite_manage(action: "remove", favouriteID: [101, 102, 103])
favourite_manage(action: "add", projectID: 5678,
                 defaultDetails: "Regular project work.")
```

## Cleanup pattern

Favourites on **closed** projects can't be logged against — they're dead weight. Offer to **remove** them
(or disable if the user wants them reversible) and to **add** a favourite for the job the person actually
logs against. Always show the list and confirm before removing. Verify with `favourite_list` after.
