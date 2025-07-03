from jewel_db.schemas.jewelry_item import JewelryItemCreate


def test_tags_validator_strips_null_and_blanks():
    payload = {"name": "Ring A", "tags": [None, "", "ruby", " "]}
    obj = JewelryItemCreate(**payload)
    assert obj.tags == ["ruby"]  # space was trimmed, None removed
