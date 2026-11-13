from quantum_dot_photodetector import slides
from quantum_dot_photodetector.summary import compute
from quantum_dot_photodetector.validation import run_all, to_markdown


def test_every_check_passes():
    rows = run_all()
    failed = [(c.num, c.category, c.name, c.model, c.expected) for c in rows if not c.passed]
    assert not failed, failed


def test_every_slide_number_is_registered_with_a_model_key():
    r = compute()
    for e in slides.REGISTRY:
        assert e.key in r
        assert (e.value is not None and e.tol is not None) or e.within is not None
        assert e.slide_text or e.script_text


def test_markdown_table_has_one_row_per_check():
    rows = run_all()
    md = to_markdown(rows)
    assert sum(1 for line in md.splitlines() if line.startswith("| ") and line[2].isdigit()) == len(rows)
