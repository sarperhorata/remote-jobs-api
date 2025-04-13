from datetime import datetime, timedelta
import logging
from typing import Dict
import json
import time

class RateLimiter:
    def __init__(self, interval_hours: int = 12):
        self.interval = timedelta(hours=interval_hours)
        self.last_run_file = 'last_run_times.json'
        self.logger = logging.getLogger(__name__)
        
    def load_last_runs(self) -> Dict:
        try:
            with open(self.last_run_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_last_runs(self, last_runs: Dict):
        with open(self.last_run_file, 'w') as f:
            json.dump(last_runs, f)

    def can_make_request(self, domain: str) -> bool:
        last_runs = self.load_last_runs()
        now = datetime.now()
        
        if domain not in last_runs:
            return True
            
        last_run = datetime.fromisoformat(last_runs[domain])
        return now - last_run >= self.interval

    def record_request(self, domain: str):
        last_runs = self.load_last_runs()
        last_runs[domain] = datetime.now().isoformat()
        self.save_last_runs(last_runs) 