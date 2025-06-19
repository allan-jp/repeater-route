# repeater-route

This tool samples a Google Maps route and looks up nearby ham-radio repeaters along the way,
using the Google Maps API and RepeaterBook’s free export API.

---

## Prerequisites

- **Python 3.8+**
- **Git**
- A **Google Maps API key** with Directions API and Geocoding API enabled
- (Optional) a **GitHub** account if you plan to push your clone

---

## Quick Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/repeater-route.git
   cd repeater-route
   ```

2. **Create & activate a virtualenv**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   # .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Copy the sample and then edit:
   ```bash
   cp .env.example .env
   ```
   Open `.env` in your editor and set:
   ```dotenv
   MAPS_API_KEY=your_real_google_maps_api_key
   MAP_INTERVAL_MILES=10         # default sampling interval in miles
   QUERY_RANGE=15                # repeater lookup radius in miles
   ROUTE_URI=                    # optional default Google Maps directions URL
   ```

5. **Run the CLI**
   - **Interval-sampling** (default, every MAP_INTERVAL_MILES):
     ```bash
     python bin/repeater_route.py -u "<GOOGLE_MAPS_DIRECTIONS_URL>"
     ```
   - **Hybrid repeater lookup** (step + 5 mi sampling):
     ```bash
     python bin/repeater_route.py -u "<GOOGLE_MAPS_DIRECTIONS_URL>" -a
     ```

---

## Project Layout

```
bin/
  repeater_route.py       # CLI entry point (bootstraps src/ onto PYTHONPATH)
src/
  repeater_route/
    cli.py                # parses args & dispatches modes
    config.py             # loads .env (API keys, intervals, etc.)
    geo.py                # haversine + interpolation
    parser.py             # parse Google Maps URL into origin/destination
    sampler.py            # sample route polyline at mile intervals
    state_lookup.py       # lat/lon → state FIPS lookup via reverse-geocode
    repeater.py           # fetch & filter repeater lists per state
    cities.py             # hybrid repeater-extraction orchestrator
.env.example              # template for your API keys & settings
requirements.txt          # pinned Python deps
pyproject.toml            # project metadata (for poetry or pip installs)
gmaps_cache.sqlite        # HTTP cache file (auto-created by requests-cache)
```

---

## Caching

All HTTP calls (both to Google Maps and RepeaterBook) are automatically cached in `gmaps_cache.sqlite` via **requests-cache**.
By default, entries never expire—so repeat runs incur zero additional network calls.

- **To clear the cache**:
  ```bash
  python - << 'EOF'
  import requests_cache
  requests_cache.clear()
  EOF
  ```

---

## License

This project is released under the **MIT License**. Feel free to adapt and extend!
