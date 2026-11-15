import sys
import pytest

CONTRACT = "contracts/plate_signal.py"
MENU = "https://menu.example.com/garden-ember"
GUIDE = "https://allergens.example.org/guide/garden-ember"


def open_report(contract):
    return contract.open_report("ember-milk", "Copper Table", "Garden Ember Bowl", "Milk", "Dairy-free", MENU, GUIDE)


def patch_now(contract, monkeypatch, callback):
    instance = object.__getattribute__(contract, "_instance")
    monkeypatch.setattr(sys.modules[instance.__class__.__module__], "_now", callback)


def result(finding="CONFLICT"):
    if finding == "CONFLICT":
        return {"finding": "CONFLICT", "severity": 91, "menu_mention": "FREE_FROM", "guide_mention": "CONTAINS", "action": "AVOID_UNTIL_CONFIRMED", "summary": "The menu claim conflicts with the allergen guide for the exact dish.", "evidence": [{"source_index": 0, "quote": "Garden Ember Bowl is dairy-free"}, {"source_index": 1, "quote": "Garden Ember Bowl contains milk"}], "source_receipts": [{"source_index": 0, "url": MENU, "host": "menu.example.com", "available": True, "sha256": "a" * 64}, {"source_index": 1, "url": GUIDE, "host": "allergens.example.org", "available": True, "sha256": "b" * 64}]}
    return {"finding": finding, "severity": 0, "menu_mention": "NOT_STATED", "guide_mention": "NOT_STATED", "action": "ASK_STAFF", "summary": "The available sources do not bind the exact dish and allergen strongly enough.", "evidence": [], "source_receipts": []}


def test_open_and_duplicate_rejected(direct_deploy):
    contract = direct_deploy(CONTRACT)
    assert open_report(contract) == "ember-milk"
    with pytest.raises(Exception):
        open_report(contract)


def test_sources_require_https_and_distinct_hosts(direct_deploy):
    contract = direct_deploy(CONTRACT)
    with pytest.raises(Exception):
        contract.open_report("bad-http", "Copper", "Bowl", "Milk", "Free", "http://menu.test/a", GUIDE)
    with pytest.raises(Exception):
        contract.open_report("same-host", "Copper", "Bowl", "Milk", "Free", "https://same.test/menu", "https://same.test/guide")


def test_review_persists_analysis_and_window(direct_deploy, monkeypatch):
    contract = direct_deploy(CONTRACT); open_report(contract)
    monkeypatch.setattr(contract, "_analyze", lambda *args: result())
    patch_now(contract, monkeypatch, lambda: 1000)
    assert contract.review_report("ember-milk")["finding"] == "CONFLICT"
    state = contract.get_report("ember-milk")
    assert state["status"] == "REVIEWED" and state["correction_deadline"] == 44200


def test_review_is_single_pass(direct_deploy, monkeypatch):
    contract = direct_deploy(CONTRACT); open_report(contract)
    monkeypatch.setattr(contract, "_analyze", lambda *args: result())
    contract.review_report("ember-milk")
    with pytest.raises(Exception):
        contract.review_report("ember-milk")


def test_only_owner_can_correct(direct_vm, direct_deploy, direct_alice, monkeypatch):
    contract = direct_deploy(CONTRACT); open_report(contract)
    monkeypatch.setattr(contract, "_analyze", lambda *args: result())
    patch_now(contract, monkeypatch, lambda: 1000); contract.review_report("ember-milk")
    direct_vm.sender = direct_alice
    with pytest.raises(Exception):
        contract.attach_correction("ember-milk", "https://third.example.net/correction", "The restaurant published a corrected allergen notice for this dish.")


def test_correction_requires_new_host_and_keeps_history(direct_deploy, monkeypatch):
    contract = direct_deploy(CONTRACT); open_report(contract)
    queue = [result(), result("INSUFFICIENT")]
    monkeypatch.setattr(contract, "_analyze", lambda *args: queue.pop(0))
    patch_now(contract, monkeypatch, lambda: 1000); contract.review_report("ember-milk")
    with pytest.raises(Exception):
        contract.attach_correction("ember-milk", "https://menu.example.com/correction", "The menu page now includes a corrected allergen claim for the item.")
    contract.attach_correction("ember-milk", "https://third.example.net/correction", "A dated correction changes the allergen wording for the exact menu item.")
    state = contract.get_report("ember-milk")
    assert state["status"] == "CORRECTED" and state["history"][0]["finding"] == "CONFLICT"


def test_expired_correction_rejected(direct_deploy, monkeypatch):
    contract = direct_deploy(CONTRACT); open_report(contract)
    monkeypatch.setattr(contract, "_analyze", lambda *args: result())
    clock = {"now": 1000}; patch_now(contract, monkeypatch, lambda: clock["now"])
    contract.review_report("ember-milk"); clock["now"] = 50000
    with pytest.raises(Exception):
        contract.attach_correction("ember-milk", "https://third.example.net/a", "This correction arrives after the protected review window has ended.")


def test_outsider_waits_but_owner_seals_early(direct_vm, direct_deploy, direct_alice, monkeypatch):
    contract = direct_deploy(CONTRACT); owner = direct_vm.sender; open_report(contract)
    monkeypatch.setattr(contract, "_analyze", lambda *args: result())
    patch_now(contract, monkeypatch, lambda: 1000); contract.review_report("ember-milk")
    direct_vm.sender = direct_alice
    with pytest.raises(Exception):
        contract.seal_report("ember-milk")
    direct_vm.sender = owner
    assert contract.seal_report("ember-milk")["status"] == "SEALED"


def test_permissionless_seal_after_window(direct_vm, direct_deploy, direct_alice, monkeypatch):
    contract = direct_deploy(CONTRACT); open_report(contract)
    monkeypatch.setattr(contract, "_analyze", lambda *args: result())
    clock = {"now": 1000}; patch_now(contract, monkeypatch, lambda: clock["now"])
    contract.review_report("ember-milk"); clock["now"] = 50000; direct_vm.sender = direct_alice
    assert len(contract.seal_report("ember-milk")["receipt"]) == 64


def test_normalizer_accepts_multiple_quotes_per_source(direct_deploy):
    contract = direct_deploy(CONTRACT)
    instance = object.__getattribute__(contract, "_instance")
    normalize = sys.modules[instance.__class__.__module__]._normalize
    fetched = [{"source_index": 0, "url": MENU, "host": "menu.example.com", "available": True, "content": "Garden Ember Bowl is dairy-free. It has no dairy ingredients.", "sha256": "a" * 64}, {"source_index": 1, "url": GUIDE, "host": "allergens.example.org", "available": True, "content": "Garden Ember Bowl contains milk. Milk is intentionally present.", "sha256": "b" * 64}]
    raw = {"finding": "CONFLICT", "severity": 91, "menu_mention": "FREE_FROM", "guide_mention": "CONTAINS", "action": "AVOID_UNTIL_CONFIRMED", "summary": "The exact dish has incompatible allergen statements in the two sources.", "evidence": [{"source_index": 0, "quote": "Garden Ember Bowl is dairy-free."}, {"source_index": 0, "quote": "It has no dairy ingredients."}, {"source_index": 1, "quote": "Garden Ember Bowl contains milk."}]}
    assert len(normalize(raw, fetched)["evidence"]) == 3
