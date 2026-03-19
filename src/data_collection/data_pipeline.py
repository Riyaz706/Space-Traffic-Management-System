"""
Data Processing Pipeline
Transforms raw satellite data into the system's standard schema
matching data/fake_satellite_data.json and writes processed JSON.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List


class DataPipeline:
    """Converts raw data to the canonical satellites schema."""

    def __init__(self,
                 raw_path: str = "data/raw_satellite_data.json",
                 processed_path: str = "data/processed_satellite_data.json"):
        self.raw_path = raw_path
        self.processed_path = processed_path

    def run(self) -> Dict[str, Any]:
        raw = self._read_raw()
        satellites = self._transform_objects(raw.get("objects", []))
        processed = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "total_objects": len(satellites),
                "data_source": ",".join(raw.get("sources", [])) or "External APIs",
                "description": "Processed live satellite dataset"
            },
            "satellites": satellites
        }
        os.makedirs(os.path.dirname(self.processed_path), exist_ok=True)
        with open(self.processed_path, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2)
        return processed

    def _read_raw(self) -> Dict[str, Any]:
        if not os.path.exists(self.raw_path):
            return {"objects": [], "sources": []}
        with open(self.raw_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {"objects": [], "sources": []}

    def _transform_objects(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for obj in objects:
            try:
                name = obj.get("name") or f"SAT-{obj.get('norad_id', 'UNKNOWN')}"
                key = self._make_key(name)
                altitude = self._safe_float(obj.get("altitude"), 500.0)
                inclination = self._safe_float(obj.get("inclination"), 45.0)
                eccentricity = self._safe_float(obj.get("eccentricity"), 0.001)
                raan = self._safe_float(obj.get("raan"), 0.0)
                arg_perigee = self._safe_float(obj.get("arg_perigee"), 0.0)
                mean_anomaly = self._safe_float(obj.get("mean_anomaly"), 0.0)
                period = self._safe_float(obj.get("period"), 95.0)

                # Determine object type heuristically
                upper_name = str(name).upper()
                if any(t in upper_name for t in ["DEBRIS", "COSMOS", "FENGYUN", "DEB"]):
                    object_type = "debris"
                else:
                    object_type = "satellite"

                result[key] = {
                    "object_type": object_type,
                    "name": name,
                    "norad_id": str(obj.get("norad_id", "")) or None,
                    "altitude": altitude,
                    "inclination": inclination,
                    "eccentricity": eccentricity,
                    "raan": raan,
                    "arg_perigee": arg_perigee,
                    "mean_anomaly": mean_anomaly,
                    "period": period,
                    "status": obj.get("status", "active"),
                    "launch_date": obj.get("launch_date"),
                    "mass": obj.get("mass"),
                    "size": obj.get("size"),
                    "operator": obj.get("operator")
                }
            except Exception:
                continue
        return result

    def _make_key(self, name: str) -> str:
        # Keep friendly names like ISS, STARLINK-1234 intact
        safe = name.strip().replace(" ", "-")
        return safe

    def _safe_float(self, value: Any, default: float) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except Exception:
            return default


def main():
    DataPipeline().run()


if __name__ == "__main__":
    main()


