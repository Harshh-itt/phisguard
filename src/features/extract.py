
import ipaddress
from urllib.parse import urlsplit


def parse_url(url: str) -> dict:
    """Parse and validate a URL without making network requests."""

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string.")

    url = url.strip()

    try:
        parsed = urlsplit(url)

        scheme = parsed.scheme.lower()

        if scheme not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are supported.")

        hostname = parsed.hostname

        if not hostname:
            raise ValueError("URL must contain a valid hostname.")

        port = parsed.port

        try:
            ipaddress.ip_address(hostname)
            is_ip_address = True
        except ValueError:
            is_ip_address = False

        return {
            "scheme": scheme,
            "hostname": hostname.lower(),
            "path": parsed.path,
            "query": parsed.query,
            "port": port,
            "is_https": int(scheme == "https"),
            "is_ip_address": int(is_ip_address),
        }

    except ValueError as error:
        raise ValueError(f"Invalid URL: {error}") from error


def extract_features(url: str) -> dict:
    """Extract deterministic static features from a URL."""

    parsed = parse_url(url)

    hostname = parsed["hostname"]

    features = {
        "url_length": len(url.strip()),
        "hostname_length": len(hostname),
        "is_https": parsed["is_https"],
        "is_ip_address": parsed["is_ip_address"],
        "digit_count": sum(char.isdigit() for char in url),
        "dot_count": hostname.count("."),
        "hyphen_count": hostname.count("-"),
        "path_length": len(parsed["path"]),
        "query_length": len(parsed["query"]),
    }

    return features
