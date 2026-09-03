"""
Asynchronous DNS resolver for mail exchange (MX) and host verification.
Uses dnspython async resolver with strict timeouts for high throughput.
"""

import dns.asyncresolver
import dns.exception
import dns.resolver
from typing import List, Dict, Any, Tuple

class DNSResolver:
    def __init__(self, timeout: float = 2.0, lifetime: float = 3.0):
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = lifetime
        # Use reliable public DNS upstreams alongside system DNS
        self.resolver.nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

    async def resolve_mx_records(self, domain: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Resolves MX records for a domain.
        RFC 5321: If no MX record is found, an A record can be used as fallback.
        Returns: (has_valid_mail_server, records_list, primary_host)
        """
        domain = domain.lower().strip()
        mx_records: List[Dict[str, Any]] = []

        try:
            answers = await self.resolver.resolve(domain, "MX")
            for rdata in answers:
                mx_records.append({
                    "preference": rdata.preference,
                    "exchange": str(rdata.exchange).rstrip(".")
                })
            # Sort by preference (lowest preference number = highest priority)
            mx_records.sort(key=lambda x: x["preference"])
            primary_host = mx_records[0]["exchange"] if mx_records else ""
            return True, mx_records, primary_host

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            # Fallback check: A record (RFC 5321 implicit MX)
            try:
                a_answers = await self.resolver.resolve(domain, "A")
                if a_answers:
                    primary_ip = str(a_answers[0])
                    return True, [{"preference": 0, "exchange": domain, "ip": primary_ip}], domain
            except Exception:
                return False, [], ""
            return False, [], ""

        except (dns.exception.Timeout, dns.resolver.NoNameservers):
            # DNS timeout / unreachable
            return False, [], "dns_timeout"

        except Exception:
            return False, [], ""

# Global singleton resolver
dns_resolver = DNSResolver()

async def check_mx(domain: str) -> Tuple[bool, List[Dict[str, Any]], str]:
    return await dns_resolver.resolve_mx_records(domain)
