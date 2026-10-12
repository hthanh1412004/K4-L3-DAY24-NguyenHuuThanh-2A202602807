"""PII must be removed before either LLM method receives ticket text."""
from agent import runner, tools


def test_all_llm_inputs_are_redacted(tmp_path, monkeypatch):
    values = ("012345678912", "0912345678", "1234567890123456", "demo@example.vn")
    text = "CCCD 012345678912; SĐT 0912345678; STK 1234567890123456; demo@example.vn"
    monkeypatch.setattr(tools, "search_docs", lambda query: [{"id": "ticket-001.md", "text": text}])

    def forbidden_read(customer_id):
        raise AssertionError("support_l1 must not read private customer records")

    monkeypatch.setattr(tools, "read_customer", forbidden_read)
    received = []

    class SpyLLM:
        def find_injection(self, content):
            received.append(content)
            return None

        def summarize(self, docs):
            received.append(docs[0]["text"])
            return "Đã tổng hợp ticket."

    assert runner.handle("ticket", SpyLLM(), log_dir=tmp_path) == "Đã tổng hợp ticket."
    assert len(received) == 2
    for content in received:
        assert all(value not in content for value in values)
        for kind in ("VN_CCCD", "VN_PHONE", "VN_BANK_ACCOUNT", "EMAIL"):
            assert f"[REDACTED_{kind}]" in content
