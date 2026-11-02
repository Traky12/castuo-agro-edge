"""Synthetic negative controls: no source access, automatic decisions, or live data."""
import math
import unittest

from evidence_bridge.bridge.sensor_decision_contract import observation_to_review_candidate


class SensorCandidateContractTest(unittest.TestCase):
    def setUp(self):
        self.input = {
            "tenant_id": "demo_tenant",
            "sensor_kind": "leaf_temperature",
            "observed_at": "2026-10-29T12:00:00+00:00",
            "value": 22.5,
            "unit": "degC",
            "source_record_sha256": "0" * 64,
        }

    def make(self, *, tenant="demo_tenant", authorized=True):
        return observation_to_review_candidate(self.input, authenticated_tenant_id=tenant,
                                               authorized_source=authorized)

    def test_never_promotes_or_executes(self):
        result = self.make()
        self.assertEqual(result["review_state"], "PENDING_HUMAN")
        self.assertFalse(result["automatic_execution"])
        self.assertFalse(result["evidence_verified"])
        self.assertIsNone(result["recommendation"])
        self.assertEqual(result["promotion"], "BLOCKED")

    def test_deterministic_candidate(self):
        self.assertEqual(self.make()["candidate_sha256"], self.make()["candidate_sha256"])

    def test_no_cross_tenant(self):
        with self.assertRaises(PermissionError):
            self.make(tenant="other_org")

    def test_no_unauthorized_source(self):
        with self.assertRaises(PermissionError):
            self.make(authorized=False)

    def test_no_untrusted_extra_fields(self):
        self.input["actuate"] = True
        with self.assertRaises(ValueError):
            self.make()

    def test_no_nonfinite_or_boolean(self):
        for value in [math.nan, math.inf, True, "23"]:
            self.input["value"] = value
            with self.assertRaises(ValueError):
                self.make()

    def test_requires_timezone_and_digest(self):
        self.input["observed_at"] = "2026-10-29T12:00:00"
        with self.assertRaises(ValueError):
            self.make()
        self.input["observed_at"] = "2026-10-29T12:00:00Z"
        self.input["source_record_sha256"] = "not-a-digest"
        with self.assertRaises(ValueError):
            self.make()

    def test_all_sensor_classes(self):
        for kind in ["fruit_diameter", "trunk_diameter", "sap_flow", "leaf_temperature", "soil_probe", "weather_station"]:
            self.input["sensor_kind"] = kind
            self.assertEqual(self.make()["sensor_kind"], kind)


if __name__ == "__main__":
    unittest.main()
