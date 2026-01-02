from app.config_settings import Config
from app.services.geolocation import GeolocationService
import os


def test_abstract_api_key_loaded_from_config_env():
    # The repository includes config/.env with ABSTRACT_API_KEY; ensure Config picks it up
    assert Config.ABSTRACT_API_KEY is not None and Config.ABSTRACT_API_KEY != ''


def test_geolocation_prints_error_when_key_missing(monkeypatch, capsys):
    # Temporarily remove the key and instantiate GeolocationService to capture the debug output
    monkeypatch.setattr('app.config_settings.Config', Config)
    monkeypatch.setenv('ABSTRACT_API_KEY', '')

    # Reload service to pick up env var change
    geo = GeolocationService()
    captured = capsys.readouterr()
    assert 'DEBUG KEY STATUS' in captured.out
    assert 'ABSTRACT_API_KEY is missing' in captured.out