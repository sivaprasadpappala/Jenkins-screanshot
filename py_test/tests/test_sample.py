def test_application_is_running():
    assert True


def test_sample_validation():
    actual = 10
    expected = 10
    assert actual == expected


def test_sample_failure():
    # Change this to True to test the successful pipeline.
    assert True, "Sample validation failed"