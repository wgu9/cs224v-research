#!/usr/bin/env python3
"""
Unit tests for events2guards.py core logic.

Tests cover the four guards (Scope, Plan, Test, Evidence) and their
combinations to ensure drift detection works correctly.
"""
import sys
import pathlib

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from tools.events2guards import calc_guards, covers_required, DEFAULT_TOOLS


def run_tests():
    """Run all test classes and report results."""
    test_classes = [
        TestScopeGuard,
        TestPlanGuard,
        TestTestGuard,
        TestEvidenceGuard,
        TestDriftScoreAndAction,
        TestPlanOnlyEvents,
        TestOverride,
        TestAutoFixable,
        TestCoversRequired
    ]

    total = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n{'=' * 60}")
        print(f"Running {test_class.__name__}")
        print(f"{'=' * 60}")

        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]

        for method_name in methods:
            total += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {method_name}")
                print(f"    AssertionError: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ {method_name}")
                print(f"    Error: {e}")
                failed += 1

    print(f"\n{'=' * 60}")
    print(f"Test Results: {passed}/{total} passed")
    if failed > 0:
        print(f"FAILED: {failed} tests failed")
        sys.exit(1)
    else:
        print("SUCCESS: All tests passed!")
        sys.exit(0)


class TestScopeGuard:
    """Test Scope Guard logic."""

    def test_file_in_allowed_paths(self):
        """File in allowed_paths → scope_guard = 0.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/main.py"}
        }
        goal = {
            "allowed_paths": ["src/**", "*.py"],
            "forbidden_paths": []
        }
        result = calc_guards(ev, goal, ".")
        assert result["scope_guard"] == 0.0

    def test_file_not_in_allowed_paths(self):
        """File NOT in allowed_paths → scope_guard = 1.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "forbidden_paths": []
        }
        result = calc_guards(ev, goal, ".")
        assert result["scope_guard"] == 1.0

    def test_file_in_forbidden_paths(self):
        """File in forbidden_paths → scope_guard = 1.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/config.py"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "forbidden_paths": ["src/config.py"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["scope_guard"] == 1.0

    def test_file_in_allowed_and_forbidden(self):
        """File in both allowed and forbidden → scope_guard = 1.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/secret.py"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "forbidden_paths": ["**/secret.py"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["scope_guard"] == 1.0

    def test_non_edit_tool_ignored(self):
        """Non-edit tools don't trigger scope guard"""
        ev = {
            "phase": "test",
            "tool": "shell",
            "cmd": "pytest"
        }
        goal = {
            "allowed_paths": ["src/**"],
            "forbidden_paths": []
        }
        result = calc_guards(ev, goal, ".")
        assert result["scope_guard"] == 0.0


class TestPlanGuard:
    """Test Plan Guard logic."""

    def test_tool_allowed_in_phase(self):
        """Tool in allowed_tools_by_phase → plan_guard = 0.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/main.py"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "allowed_tools_by_phase": {
                "modify": ["edit", "shell", "plan"]
            }
        }
        result = calc_guards(ev, goal, ".")
        assert result["plan_guard"] == 0.0

    def test_tool_not_allowed_in_phase(self):
        """Tool NOT in allowed_tools_by_phase → plan_guard = 1.0"""
        ev = {
            "phase": "reproduce",
            "tool": "edit",
            "where": {"path": "src/main.py"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "allowed_tools_by_phase": {
                "reproduce": ["shell", "browse", "plan"]  # edit not allowed
            }
        }
        result = calc_guards(ev, goal, ".")
        assert result["plan_guard"] == 1.0

    def test_edit_file_not_allowed(self):
        """Edit tool but file not in allowed_paths → plan_guard = 1.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "allowed_tools_by_phase": {
                "modify": ["edit", "shell"]
            }
        }
        result = calc_guards(ev, goal, ".")
        assert result["plan_guard"] == 1.0

    def test_default_tools_used_when_not_specified(self):
        """Use DEFAULT_TOOLS when allowed_tools_by_phase not in goal"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/main.py"}
        }
        goal = {
            "allowed_paths": ["src/**"]
            # allowed_tools_by_phase not specified
        }
        result = calc_guards(ev, goal, ".")
        # DEFAULT_TOOLS["modify"] includes "edit"
        assert result["plan_guard"] == 0.0


class TestTestGuard:
    """Test Test Guard logic."""

    def test_required_test_run(self):
        """Required test in cmd → test_guard = 0.0"""
        ev = {
            "phase": "test",
            "tool": "shell",
            "cmd": "pytest -k test_auth"
        }
        goal = {
            "required_tests": ["test_auth"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["test_guard"] == 0.0

    def test_required_test_not_run(self):
        """Required test NOT in cmd → test_guard = 1.0"""
        ev = {
            "phase": "test",
            "tool": "shell",
            "cmd": "pytest -k test_other"
        }
        goal = {
            "required_tests": ["test_auth"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["test_guard"] == 1.0

    def test_no_required_tests(self):
        """No required_tests specified → test_guard = 0.0"""
        ev = {
            "phase": "test",
            "tool": "shell",
            "cmd": "pytest"
        }
        goal = {
            "required_tests": []
        }
        result = calc_guards(ev, goal, ".")
        assert result["test_guard"] == 0.0

    def test_regress_phase_test_guard(self):
        """Test guard applies to regress phase too"""
        ev = {
            "phase": "regress",
            "tool": "shell",
            "cmd": "npm test"
        }
        goal = {
            "required_tests": ["test_auth"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["test_guard"] == 1.0

    def test_non_test_phase_ignored(self):
        """Non-test/regress phases don't trigger test guard"""
        ev = {
            "phase": "modify",
            "tool": "shell",
            "cmd": "echo hello"
        }
        goal = {
            "required_tests": ["test_auth"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["test_guard"] == 0.0


class TestEvidenceGuard:
    """Test Evidence Guard logic."""

    def test_modify_edit_with_evidence(self):
        """modify + edit + evidence → evidence_guard = 0.0"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/auth.py"},
            "evidence": {
                "tests": ["test_auth.py::test_login"]
            }
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["evidence_guard"] == 0.0

    def test_modify_edit_without_evidence(self):
        """modify + edit + no evidence → evidence_guard = 0.5"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/auth.py"}
            # No evidence field
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["evidence_guard"] == 0.5

    def test_evidence_with_logs(self):
        """Evidence can be logs"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/auth.py"},
            "evidence": {
                "logs": ["error.log"]
            }
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["evidence_guard"] == 0.0

    def test_evidence_with_links(self):
        """Evidence can be links"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/auth.py"},
            "evidence": {
                "links": ["https://github.com/issue/123"]
            }
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["evidence_guard"] == 0.0

    def test_non_modify_phase_ignored(self):
        """Non-modify phases don't need evidence"""
        ev = {
            "phase": "test",
            "tool": "edit",
            "where": {"path": "test/test_auth.py"}
        }
        goal = {
            "allowed_paths": ["test/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["evidence_guard"] == 0.0


class TestDriftScoreAndAction:
    """Test drift score calculation and action determination."""

    def test_no_drift(self):
        """All guards pass → drift_score = 0.0, action = ok"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "src/main.py"},
            "evidence": {"tests": ["test_main.py"]}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "allowed_tools_by_phase": {"modify": ["edit", "shell"]}
        }
        result = calc_guards(ev, goal, ".")
        assert result["drift_score"] == 0.0
        assert result["action"] == "ok"

    def test_scope_drift_causes_warn(self):
        """Scope violation → drift_score >= warn threshold"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"}  # not in allowed
        }
        goal = {
            "allowed_paths": ["src/**"],
            "weights": {"scope": 0.4, "plan": 0.3, "test": 0.2, "evidence": 0.1},
            "thresholds": {"warn": 0.3, "rollback": 0.8}
        }
        result = calc_guards(ev, goal, ".")
        # scope=1.0 * weight=0.4 = 0.4 drift
        assert result["drift_score"] >= 0.3
        assert result["action"] == "warn"

    def test_multiple_violations_cause_rollback(self):
        """Multiple violations → drift_score >= rollback threshold"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"}  # scope + plan violation
        }
        goal = {
            "allowed_paths": ["src/**"],
            "weights": {"scope": 0.4, "plan": 0.3, "test": 0.2, "evidence": 0.1},
            "thresholds": {"warn": 0.5, "rollback": 0.8}
        }
        result = calc_guards(ev, goal, ".")
        # scope=1.0 * 0.4 + plan=1.0 * 0.3 + evidence=0.5 * 0.1 = 0.75
        # If drift >= 0.8, should be rollback, otherwise warn
        assert result["action"] in ["warn", "rollback"]

    def test_custom_weights(self):
        """Custom weights affect drift calculation"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"}
        }
        goal = {
            "allowed_paths": ["src/**"],
            "weights": {"scope": 1.0, "plan": 0.0, "test": 0.0, "evidence": 0.0},
            "thresholds": {"warn": 0.5, "rollback": 1.0}
        }
        result = calc_guards(ev, goal, ".")
        # scope=1.0 * weight=1.0 = 1.0 drift
        assert result["drift_score"] == 1.0
        assert result["action"] == "rollback"


class TestPlanOnlyEvents:
    """Test plan-only events (tool='plan')."""

    def test_plan_event_ignored(self):
        """Plan events get all guards = 0.0"""
        ev = {
            "phase": "modify",
            "tool": "plan",
            "where": {"path": "src/main.py"}
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["scope_guard"] == 0.0
        assert result["plan_guard"] == 0.0
        assert result["test_guard"] == 0.0
        assert result["evidence_guard"] == 0.0
        assert result["drift_score"] == 0.0
        assert result["action"] == "ok"
        assert result["notes"] == "plan-only (ignored)"


class TestOverride:
    """Test override logic."""

    def test_acknowledged_override_reduces_drift(self):
        """Acknowledged override reduces scope/plan/evidence"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"},
            "override": {
                "acknowledged": True,
                "reason": "User requested dependency update"
            }
        }
        goal = {
            "allowed_paths": ["src/**"],
            "weights": {"scope": 0.4, "plan": 0.3, "test": 0.2, "evidence": 0.1}
        }
        result = calc_guards(ev, goal, ".")
        # scope capped at 0.2, plan capped at 0.2, evidence capped at 0.1
        assert result["scope_guard"] <= 0.2
        assert result["plan_guard"] <= 0.2
        assert result["evidence_guard"] <= 0.1


class TestAutoFixable:
    """Test auto_fixable and fix_cmd generation."""

    def test_scope_violation_auto_fixable(self):
        """Scope violation on edit → auto_fixable = True"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"}
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["auto_fixable"] == True
        assert result["fix_cmd"] == "git checkout -- requirements.txt"

    def test_acknowledged_not_auto_fixable(self):
        """Acknowledged override prevents auto_fixable"""
        ev = {
            "phase": "modify",
            "tool": "edit",
            "where": {"path": "requirements.txt"},
            "override": {"acknowledged": True}
        }
        goal = {
            "allowed_paths": ["src/**"]
        }
        result = calc_guards(ev, goal, ".")
        assert result["auto_fixable"] == False


class TestCoversRequired:
    """Test covers_required helper function."""

    def test_exact_match(self):
        assert covers_required("pytest -k test_auth", ["test_auth"]) == True

    def test_partial_match(self):
        assert covers_required("pytest tests/test_auth.py", ["test_auth"]) == True

    def test_case_insensitive(self):
        assert covers_required("PYTEST -k TEST_AUTH", ["test_auth"]) == True

    def test_no_match(self):
        assert covers_required("pytest -k test_other", ["test_auth"]) == False

    def test_empty_required(self):
        assert covers_required("pytest", []) == True

    def test_multiple_required_one_matches(self):
        assert covers_required("pytest -k test_auth", ["test_auth", "test_login"]) == True

    def test_multiple_required_none_match(self):
        assert covers_required("pytest -k test_other", ["test_auth", "test_login"]) == False


if __name__ == "__main__":
    run_tests()
