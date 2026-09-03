"""
High-performance in-memory disposable and temporary email domain checker.
Loads curated domain lists and supports fast exact & subdomain matching.
"""

import os
from typing import Set

class DisposableFilter:
    def __init__(self, data_file_path: str = None):
        if data_file_path is None:
            # Default to data/disposable_domains.txt relative to this module
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_file_path = os.path.join(base_dir, "data", "disposable_domains.txt")
        
        self.disposable_domains: Set[str] = self._load_domains(data_file_path)

    def _load_domains(self, file_path: str) -> Set[str]:
        domains = set()
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip().lower()
                    if clean_line and not clean_line.startswith("#"):
                        domains.add(clean_line)
        return domains

    def is_disposable(self, domain: str) -> bool:
        """
        Checks if a domain or any of its parent domains is a known throwaway provider.
        E.g., 'sub.mailinator.com' -> checks 'sub.mailinator.com' then 'mailinator.com'
        """
        if not domain:
            return False
        
        domain = domain.lower().strip()
        parts = domain.split(".")

        # Check full domain first
        if domain in self.disposable_domains:
            return True

        # Check parent domains (subdomain matching)
        for i in range(1, len(parts) - 1):
            parent_domain = ".".join(parts[i:])
            if parent_domain in self.disposable_domains:
                return True

        return False

# Global singleton instance for maximum performance
filter_instance = DisposableFilter()

def is_disposable_domain(domain: str) -> bool:
    return filter_instance.is_disposable(domain)
