from spyral_utils.nuclear import ParticleID, deserialize_particle_id, NuclearDataMap
from pathlib import Path

PID_JSON_PATH: Path = Path(__file__).parent.resolve() / "pid.json"


def test_pid():
    nuc_map = NuclearDataMap()
    pid = deserialize_particle_id(PID_JSON_PATH, nuc_map)

    assert isinstance(pid, ParticleID)
    assert pid.cut.is_point_inside(0.5, 0.5)
    assert not pid.cut.is_point_inside(-1.0, -1.0)
    assert pid.nucleus.Z == 6
    assert pid.nucleus.A == 12
