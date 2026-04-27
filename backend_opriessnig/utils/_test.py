def test() -> None:
    print("This is a test!")


# Prevent pytest from collecting this helper as a real test function.
test.__test__ = False
