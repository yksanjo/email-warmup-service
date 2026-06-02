import importlib.util
from pathlib import Path

# Load warmup.py (top-level module file, not a package).
_spec = importlib.util.spec_from_file_location(
    "warmup", Path(__file__).resolve().parent.parent / "warmup.py"
)
warmup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(warmup)


def _service(tmp_path, **env):
    import os

    for key, value in env.items():
        os.environ[key] = str(value)
    svc = warmup.EmailWarmupService()
    svc.state_file = str(tmp_path / "state.json")
    return svc


def test_imports_service():
    assert hasattr(warmup, "EmailWarmupService")


def test_volume_curve_is_monotonic_and_bounded(tmp_path):
    svc = _service(
        tmp_path, WARMUP_DURATION_DAYS=30, INITIAL_VOLUME=5, TARGET_VOLUME=100
    )

    assert svc.calculate_daily_volume(0) == 0
    assert svc.calculate_daily_volume(-1) == 0

    # Ramp starts at/above the initial volume and ends at the target.
    assert svc.calculate_daily_volume(1) >= 5
    assert svc.calculate_daily_volume(30) == 100

    # Volume never decreases across the warm-up window.
    prev = -1
    for day in range(1, 31):
        v = svc.calculate_daily_volume(day)
        assert v >= prev
        assert 5 <= v <= 100
        prev = v


def test_initial_state(tmp_path):
    svc = _service(tmp_path)
    assert svc.state["started"] is False
    assert svc.state["total_emails_sent"] == 0
