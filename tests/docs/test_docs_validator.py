import uuid
from pathlib import Path

from utils.docs_validator import validate_docs


def test_validator_detects_broken_link_and_kebab():
    # Use a repo-local temp area to avoid Windows TMP permission issues
    base = Path("docs/System_layout/_raw/_tmp_docs_validator") / f"case-{uuid.uuid4()}"
    base.mkdir(parents=True, exist_ok=True)

    # Good file
    (base / "good-file.md").write_text("# Hello\nSee [Other](other-file.md)\n", encoding="utf-8")
    # Missing target to trigger broken link
    # (base / "other-file.md") is intentionally absent

    # Bad filename style
    (base / "Bad_Name.md").write_text("# Bad\n", encoding="utf-8")

    report = validate_docs(str(base))
    assert report["counts"]["markdown"] == 2
    assert any(it["type"] == "broken_link" for it in report["link_issues"])  # broken link exists
    assert any(it["type"] == "kebab_case" for it in report["name_issues"])  # wrong file name detected

