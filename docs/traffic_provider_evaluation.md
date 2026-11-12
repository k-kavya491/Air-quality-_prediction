# Traffic provider evaluation

| Provider | Data | Authentication | Free usage | Notes |
|---|---|---|---|---|
| TomTom Traffic Flow (Flow Segment Data) | Current speed, free-flow speed, travel times, confidence, road closure for the nearest road segment | API key in the request | 2,500 non-tile requests per day, no credit card (TomTom pricing page) | Chosen. Coverage must be tested for each city |
| Google Maps (Directions with traffic) | Travel time in traffic for a route | API key | Billing account required before a key works | Rejected: needs a billing account |
| HERE Traffic | Flow and incidents | API key | Freemium plan, check current limits | Alternative if TomTom has no coverage |
| Mapbox Directions (driving-traffic) | Route travel time with traffic | Access token | Monthly free allowance, check current limits | Route-based, not point-based |
| Azure Maps Traffic v1 | Flow segment data | Key | n/a | Not used: Microsoft's page announces a v1 retirement |

## Decision

TomTom Flow Segment Data. It takes a latitude and longitude, needs only a key, and its free allowance covers this project.

## Limitations

- The result describes the nearest road segment, so it is a proxy for local traffic, not area-wide density.
- Points far from a mapped road return an error, which the application reports as "no traffic data".
- The free API has no history, so traffic is only stored when the scheduler collects it.
- Quota use: tracked cities collected hourly use about 24 requests per city per day.