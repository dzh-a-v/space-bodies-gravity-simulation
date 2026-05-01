from gravity_sim.benchmark import benchmark_counts, generate_benchmark_bodies


def test_generate_benchmark_bodies_creates_valid_unique_bodies():
    bodies = generate_benchmark_bodies(10)

    assert len(bodies) == 10
    assert len({body.name for body in bodies}) == 10
    assert len({body.color for body in bodies}) == 10


def test_benchmark_counts_returns_hotspot_metrics():
    rows = benchmark_counts(counts=(5,), repeats=1)

    assert rows[0]["n"] == 5
    assert rows[0]["gravity_ms"] >= 0.0
    assert rows[0]["verlet_ms"] >= 0.0
    assert rows[0]["collisions_ms"] >= 0.0
    assert rows[0]["roche_ms"] >= 0.0
