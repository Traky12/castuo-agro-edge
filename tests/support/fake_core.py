"""In-memory stand-in for the core ingest endpoint, shared by the gateway tests.

It deduplicates by event_id, as the real core must, and can misbehave on purpose.
It is a SIMULATION: it proves the edge side of the contract, not the real core
(CORE-006, persistence in Castuo-system, is not exercised by any test here).
"""
import requests


class Response:
    def __init__(self, status_code):
        self.status_code = status_code


class FakeCore:
    """In-memory core that stores events by event_id and can misbehave on purpose."""

    def __init__(self):
        self.online = True
        self.events = {}          # event_id -> body
        self.deliveries = []      # every POST that reached the core
        self.lose_ack_times = 0   # store the event, then fail before the client sees 2xx
        self.fail_with_500 = 0

    def post(self, url, json=None, headers=None, timeout=None):
        if not self.online:
            raise requests.ConnectionError("network down")
        if self.fail_with_500:
            self.fail_with_500 -= 1
            return Response(500)
        body = json
        assert headers["Idempotency-Key"] == body["event_id"]
        self.deliveries.append(body)
        stable = {k: v for k, v in body.items() if k != "gateway_ts"}
        previous = self.events.get(body["event_id"])
        assert previous is None or {k: v for k, v in previous.items() if k != "gateway_ts"} == stable, "same event_id with a different event"
        self.events[body["event_id"]] = body
        if self.lose_ack_times:
            self.lose_ack_times -= 1
            raise requests.ConnectionError("connection lost after the core stored the event")
        return Response(201 if previous is None else 200)
