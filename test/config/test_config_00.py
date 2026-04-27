import backend_opriessnig


def test_config_00() -> None:
    config = backend_opriessnig.config.Config.get_instance()
    assert config

    assert "sqlite:///:memory:" == config.connection_string
