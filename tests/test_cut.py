from spyral_utils.plot import Cut2D, deserialize_cut, CutHandler
from pathlib import Path

CUT_JSON_PATH: Path = Path(__file__).parent.resolve() / "cut.json"


def test_cut():
    cut = deserialize_cut(CUT_JSON_PATH)
    handler = CutHandler()

    assert isinstance(cut, Cut2D)
    assert cut.is_point_inside(0.5, 0.5)
    assert not cut.is_point_inside(-1.0, -1.0)
