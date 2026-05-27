from bank_demo.mock_data import lookup_customer_id


def test_lookup_customer_id_case_insensitive():
    assert lookup_customer_id("cust-1001") == "CUST-1001"
    assert lookup_customer_id("CUST-1002") == "CUST-1002"
    assert lookup_customer_id("  cust-1003  ") == "CUST-1003"


def test_lookup_customer_id_not_found():
    assert lookup_customer_id("CUST-9999") is None
    assert lookup_customer_id("") is None
