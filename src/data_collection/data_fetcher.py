"""
Data Fetcher Module
Fetches real-time satellite data from external APIs and saves raw JSON.
"""

import asyncio
import json
import os
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

import aiohttp


class DataFetcher:
    """Fetches satellite data from external sources and saves raw JSON."""

    def __init__(self, output_path: str = "data/raw_satellite_data.json"):
        self.output_path = output_path
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def fetch(self, target_count: int = 50) -> Dict[str, Any]:
        """
        Fetch data from multiple sources and return aggregated raw data.
        Raw schema:
        {
          "fetched_at": iso8601,
          "sources": ["N2YO", "Open-Notify", ...],
          "objects": [ { ... raw fields ... } ]
        }
        """
        aggregated: Dict[str, Any] = {
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "sources": [],
            "objects": []
        }

        # Primary: Celestrak GP JSON across multiple groups to reach target_count
        try:
            celestrak_objects = await self._fetch_celestrak_gp_multi(target_count)
            if celestrak_objects:
                aggregated["sources"].append("Celestrak-GP-Multi")
                aggregated["objects"].extend(celestrak_objects)
        except Exception:
            pass

        try:
            iss_object = await self._fetch_open_notify_iss()
            if iss_object:
                aggregated["sources"].append("Open-Notify")
                aggregated["objects"].append(iss_object)
        except Exception:
            pass

        # Secondary fallback: N2YO demo if we still have few objects
        if len(aggregated["objects"]) < max(1, target_count // 2):
            try:
                n2yo_objects = await self._fetch_n2yo_demo()
                if n2yo_objects:
                    aggregated["sources"].append("N2YO-demo")
                    aggregated["objects"].extend(n2yo_objects)
            except Exception:
                pass

        # Trim or sample to requested count (keep ISS if present)
        if aggregated["objects"]:
            # Preserve ISS if present, then sample the rest
            iss_list = [o for o in aggregated["objects"] if str(o.get("norad_id")) == "25544"]
            others = [o for o in aggregated["objects"] if str(o.get("norad_id")) != "25544"]
            k = max(0, target_count - len(iss_list))
            sampled_others = random.sample(others, k=min(k, len(others)))
            aggregated["objects"] = (iss_list + sampled_others)[:target_count]

        # Ensure at least one object (fallback minimal ISS-like sample)
        if not aggregated["objects"]:
            aggregated["objects"].append({
                "name": "International Space Station (fallback)",
                "norad_id": "25544",
                "latitude": 0.0,
                "longitude": 0.0,
                "altitude": 408.0,
                "velocity": 7.66,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })

        # Persist raw data
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(aggregated, f, indent=2)

        return aggregated

    async def _fetch_celestrak_gp_multi(self, target_count: int) -> List[Dict[str, Any]]:
        """Fetch from multiple Celestrak GP groups until reaching target_count.

        Docs: https://celestrak.org/NORAD/elements/gp.php
        Example: https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json
        """
        if self.session is None:
            return []

        groups = [
            "active",
            "starlink",
            "oneweb",
            "iridium",
            "gps-ops",
            "galileo",
            "glonass",
            "beidou",
            "visual",
            "last-30-days"
        ]

        # Collect and deduplicate by NORAD_CAT_ID
        seen: set = set()
        collected_raw: List[Dict[str, Any]] = []
        for g in groups:
            url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={g}&FORMAT=json"
            try:
                async with self.session.get(url, timeout=20) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
            except Exception:
                continue
            items = data if isinstance(data, list) else []
            for sat in items:
                norad_val = sat.get("NORAD_CAT_ID")
                if norad_val is None:
                    continue
                if norad_val in seen:
                    continue
                seen.add(norad_val)
                collected_raw.append(sat)
                if len(collected_raw) >= target_count:
                    break
            if len(collected_raw) >= target_count:
                break

        if not collected_raw:
            return []

        # If more than needed, sample down; else keep as-is
        if len(collected_raw) > target_count:
            collected_raw = random.sample(collected_raw, target_count)

        # Convert to unified raw objects
        mu_earth = 398600.4418  # km^3/s^2
        earth_radius = 6378.137 # km
        objects: List[Dict[str, Any]] = []
        for sat in collected_raw:
            try:
                name = sat.get("OBJECT_NAME")
                norad = str(sat.get("NORAD_CAT_ID")) if sat.get("NORAD_CAT_ID") is not None else None
                incl = float(sat.get("INCLINATION", 0.0))
                ecc = float(sat.get("ECCENTRICITY", 0.0))
                raan = float(sat.get("RAAN", 0.0))
                argp = float(sat.get("ARG_OF_PERICENTER", 0.0))
                mo = float(sat.get("MEAN_ANOMALY", 0.0))
                n_rev_per_day = float(sat.get("MEAN_MOTION", 15.0))

                period_minutes = 1440.0 / n_rev_per_day if n_rev_per_day > 0 else 95.0
                n_rad_s = n_rev_per_day * 2.0 * 3.141592653589793 / 86400.0
                a_km = (mu_earth / (n_rad_s ** 2)) ** (1.0 / 3.0) if n_rad_s > 0 else earth_radius + 500.0
                alt_km = max(0.0, a_km - earth_radius)
                vel_km_s = (mu_earth / a_km) ** 0.5 if a_km > 0 else 7.6

                objects.append({
                    "name": name,
                    "norad_id": norad,
                    "inclination": incl,
                    "eccentricity": ecc,
                    "raan": raan,
                    "arg_perigee": argp,
                    "mean_anomaly": mo,
                    "period": period_minutes,
                    "altitude": alt_km,
                    "velocity": vel_km_s,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "Celestrak-GP"
                })
            except Exception:
                continue
        return objects

    async def _fetch_n2yo_demo(self) -> List[Dict[str, Any]]:
        if self.session is None:
            return []
        url = "https://api.n2yo.com/rest/v1/satellite/above/0/0/0/70/&apiKey=demo"
        try:
            async with self.session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
        except Exception:
            return []

        objects: List[Dict[str, Any]] = []
        above = data.get("above", []) if isinstance(data, dict) else []
        for sat in above:
            try:
                objects.append({
                    "name": sat.get("satname"),
                    "norad_id": str(sat.get("satid")),
                    "latitude": sat.get("satlat"),
                    "longitude": sat.get("satlng"),
                    "altitude": sat.get("satalt"),
                    "velocity": None,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "N2YO"
                })
            except Exception:
                continue
        return objects

    async def _fetch_open_notify_iss(self) -> Optional[Dict[str, Any]]:
        if self.session is None:
            return None
        url = "http://api.open-notify.org/iss-now.json"
        try:
            async with self.session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
        except Exception:
            return None

        try:
            pos = data.get("iss_position", {})
            ts = data.get("timestamp")
            return {
                "name": "International Space Station",
                "norad_id": "25544",
                "latitude": float(pos.get("latitude")),
                "longitude": float(pos.get("longitude")),
                "altitude": 408.0,
                "velocity": 7.66,
                "timestamp": datetime.utcfromtimestamp(ts).isoformat() + "Z",
                "source": "Open-Notify"
            }
        except Exception:
            return None


async def main():
    async with DataFetcher() as fetcher:
        await fetcher.fetch()


if __name__ == "__main__":
    asyncio.run(main())


