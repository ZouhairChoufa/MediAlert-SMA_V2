import pytest
from unittest.mock import patch, Mock
from app.services.geolocation import GeolocationService


def test_nominatim_user_agent_used_and_success():
    geo = GeolocationService()
    address = "Av Khalil Jabran, El Jadida"

    # Ensure we don't hit AbstractAPI path in this test
    geo.abstract_api_key = None

    fake_json = [{'lat': '33.2564', 'lon': '-8.5106', 'display_name': 'Av Khalil Jabran, El Jadida'}]

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_json
    mock_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_resp) as mock_get:
        result = geo.geocode_address(address)

        assert result is not None
        assert result['lat'] == 33.2564
        assert result['lng'] == -8.5106
        assert result['source'] == 'nominatim'

        # Verify requests.get was called with headers containing the correct User-Agent
        mock_get.assert_called()
        _, called_kwargs = mock_get.call_args
        assert 'headers' in called_kwargs
        assert called_kwargs['headers'] == {'User-Agent': 'EmergencyApp/1.0'}


def test_nominatim_403_falls_back_to_morocco():
    geo = GeolocationService()
    address = "Av Khalil Jabran, El Jadida"
    geo.abstract_api_key = None

    # Simulate a 403 Forbidden from Nominatim
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = Exception('403 Client Error: Forbidden')

    with patch('requests.get', return_value=mock_resp) as mock_get:
        result = geo.geocode_address(address)

        # Expect fallback to Morocco locations
        assert result is not None
        assert result['source'] == 'fallback'
        assert result['lat'] == 33.2564
        assert result['lng'] == -8.5106


def test_nominatim_includes_email_param_when_configured():
    geo = GeolocationService()
    address = "Av Khalil Jabran, El Jadida"
    geo.abstract_api_key = None

    # Configure an email for Nominatim
    geo.nominatim_email = 'dev@example.com'

    fake_json = [{'lat': '33.2564', 'lon': '-8.5106', 'display_name': 'Av Khalil Jabran, El Jadida'}]

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_json
    mock_resp.raise_for_status.return_value = None

    with patch('requests.get', return_value=mock_resp) as mock_get:
        result = geo.geocode_address(address)

        assert result is not None
        assert result['source'] == 'nominatim'

        # Verify requests.get was called with params containing the email
        mock_get.assert_called()
        _, called_kwargs = mock_get.call_args
        assert 'params' in called_kwargs
        assert called_kwargs['params'].get('email') == 'dev@example.com'