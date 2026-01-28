from fun import have_fun


def test_have_more_fun(some_fun: str) -> None:
    """Test the have_fun function."""
    print(f"\n👍 Using fixture value: {some_fun}")
    actual = have_fun(17)
    # count number of "fun" in actual
    fun_count = actual.count("fun")
    assert fun_count == 17
