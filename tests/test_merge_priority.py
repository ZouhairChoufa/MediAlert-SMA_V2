from app.services.geolocation import GeolocationService
from unittest.mock import Mock, patch
import requests


def test_manual_overrides_gps_with_coords():
    geo = GeolocationService()

    gps = {'lat': 1.0, 'lng': 2.0}
    manual = {'address': 'Test Address', 'lat': 10.0, 'lng': 20.0}

    result = geo.merge_all_location_sources(gps=gps, manual=manual, ip=None)

    assert result['source'] == 'manual'
    assert result['lat'] == 10.0
    assert result['lng'] == 20.0


def test_manual_address_returns_manual_without_geocoding():
    geo = GeolocationService()

    gps = {'lat': 1.0, 'lng': 2.0}
    manual = {'address': 'Just an address', 'lat': None, 'lng': None}

    result = geo.merge_all_location_sources(gps=gps, manual=manual, ip=None)

    assert result['source'] == 'manual'
    assert result.get('lat') is None
    assert result.get('lng') is None
    assert result['address'] == 'Just an address'


def test_gps_used_when_no_manual():
    geo = GeolocationService()

    gps = {'lat': 5.5, 'lng': 6.6}
    manual = None

    result = geo.merge_all_location_sources(gps=gps, manual=manual, ip=None)

    assert result['source'] == 'gps'
    assert result['lat'] == 5.5
    assert result['lng'] == 6.6


def test_abstractapi_dns_failure_falls_back_to_nominatim():
    geo = GeolocationService()
    geo.abstract_api_key = 'fake-key'

    # Setup responses: AbstractAPI call will raise a RequestException (DNS), Nominatim returns valid JSON
    def fake_requests_get(url, params=None, headers=None, timeout=None):
        if url.startswith(geo.abstract_geocode_url.rstrip('/')):
            raise requests.exceptions.RequestException('Failed to resolve host')
        elif url.startswith(geo.nominatim_url_search):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = [{'lat': '33.2564', 'lon': '-8.5106', 'display_name': 'Av Khalil Jabran, El Jadida'}]
            mock_resp.text = '{"lat":"33.2564","lon":"-8.5106"}'
            return mock_resp
        raise RuntimeError('Unexpected URL')

    with patch('requests.get', side_effect=fake_requests_get) as mocked:
        result = geo.geocode_address('Av Khalil Jabran, El Jadida')
        assert result is not None
        assert result['source'] in ('nominatim', 'fallback')
        # If nominatim returned valid, expect its coords
        assert result.get('lat') == 33.2564
        assert result.get('lng') == -8.5106