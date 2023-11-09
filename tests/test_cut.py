from spyral_utils.plot import Cut2D, load_cut_json
from pathlib import Path

CUT_JSON_PATH: Path = Path(__file__).parent.resolve() / 'cut.json'

def test_cut():
    cut = load_cut_json(CUT_JSON_PATH)

    assert isinstance(cut, Cut2D)
    assert cut.is_point_inside(0.5, 0.5)