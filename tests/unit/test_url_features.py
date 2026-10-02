
import pytest

from src.features.extract import extract_features, parse_url


def test_valid_https_url():
    result = parse_url("https://example.com/login")

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/login"
    assert result["is_https"] == 1
    assert result["is_ip_address"] == 0


def test_valid_http_url():
    result = parse_url("http://example.com")

    assert result["scheme"] == "http"
    assert result["is_https"] == 0


def test_ip_address():
    result = parse_url("https://192.168.1.1")

    assert result["is_ip_address"] == 1


def test_missing_scheme():
    with pytest.raises(ValueError):
        parse_url("example.com/login")


def test_unsupported_scheme():
    with pytest.raises(ValueError):
        parse_url("ftp://example.com")


def test_empty_url():
    with pytest.raises(ValueError):
        parse_url("")


def test_missing_hostname():
    with pytest.raises(ValueError):
        parse_url("https:///login")


def test_invalid_port():
    with pytest.raises(ValueError):
        parse_url("https://example.com:abc")





def test_extract_features_from_https_url():
    features = extract_features("https://example123.com/login?id=10")

    assert features["url_length"] == len(
        "https://example123.com/login?id=10"
    )
    assert features["hostname_length"] == len("example123.com")
    assert features["is_https"] == 1
    assert features["is_ip_address"] == 0
    assert features["digit_count"] == 5
    assert features["dot_count"] == 1
    assert features["hyphen_count"] == 0
    assert features["path_length"] == 6
    assert features["query_length"] == 5


def test_extract_features_from_http_url():
    features = extract_features("http://example.com")

    assert features["is_https"] == 0
    assert features["path_length"] == 0
    assert features["query_length"] == 0


def test_extract_features_from_ip_url():
    features = extract_features("https://192.168.1.1/login")

    assert features["is_ip_address"] == 1
    assert features["dot_count"] == 3


def test_valid_port():
    result = parse_url("https://example.com:8080/login")

    assert result["hostname"] == "example.com"
    assert result["port"] == 8080


def test_port_out_of_range():
    with pytest.raises(ValueError):
        parse_url("https://example.com:70000")


def test_ipv6_address():
    result = parse_url("https://[2001:db8::1]/login")

    assert result["is_ip_address"] == 1
    assert result["hostname"] == "2001:db8::1"


def test_whitespace_inside_hostname():
    with pytest.raises(ValueError):
        parse_url("https://bad host.com/login")


def test_non_string_url():
    with pytest.raises(ValueError):
        parse_url(123)


def test_url_with_query_and_fragment():
    result = parse_url(
        "https://example.com/search?q=test#section"
    )

    assert result["path"] == "/search"
    assert result["query"] == "q=test"

def test_hostname_with_invalid_character():
    with pytest.raises(ValueError):
        parse_url("https://exam ple.com")


def test_hostname_with_empty_label():
    with pytest.raises(ValueError):
        parse_url("https://example..com")


def test_invalid_ipv4_address():
    with pytest.raises(ValueError):
        parse_url("https://999.999.999.999")
