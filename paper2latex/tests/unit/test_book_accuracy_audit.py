from __future__ import annotations

import json
from pathlib import Path

import fitz
import pytest

from scripts import audit_book_accuracy as audit_module
from scripts.audit_book_accuracy import (
    attach_source_hashes,
    audit_status,
    bind_files,
    bind_tree,
    binding_errors,
    book_delivery_binding,
    create_tree,
    evidence_hash,
    example_boundary_source_ids,
    expected_count_errors,
    explicit_source_ids,
    formal_example_count,
    hash_bytes,
    inside,
    install,
    installed_delivery_errors,
    materialize_master,
    overlap_ratio,
    persisted_build_findings,
    render_and_compare,
    resolve_page_span,
    resource_source_ids,
    rows_from_html,
    safe_book,
    source_exclusions,
    span_for_content,
    sync_status,
    tree_binding_errors,
    uncovered_source_blocks,
    validate_corrections,
    verification_report,
)
from scripts.repair_evolution_source_coverage import append_provenance


def test_safe_book_rejects_path_escape() -> None:
    with pytest.raises(ValueError):
        safe_book("../PopGen")
    assert safe_book("PopGen") == "PopGen"


def test_inside_rejects_sibling_path(tmp_path: Path) -> None:
    root = tmp_path / "book_audits"
    assert inside(root / "PopGen", root)
    assert not inside(tmp_path / "outside", root)


def test_create_tree_uses_standard_layout(tmp_path: Path) -> None:
    audit = tmp_path / "PopGen"
    create_tree(audit)
    for relative in (
        "source/pages", "source/normalized_layout", "evidence/page_contacts",
        "evidence/crops/formulas", "evidence/contacts/figures", "ledgers",
        "review", "corrections", "staging/data", "snapshots/preinstall",
        "reports", "logs", "failures",
    ):
        assert (audit / relative).is_dir()


def test_hash_change_invalidates_verified_review() -> None:
    status = {kind: {} for kind in ("pages", "blocks", "formulas", "tables", "figures", "examples")}
    status["pages"]["59"] = {"status": "verified", "evidence_sha256": "old"}
    result = sync_status(status, {"pages": [{"review_key": "59", "evidence_sha256": "new"}]})
    assert result["pages"]["59"] == {"status": "stale", "evidence_sha256": "new"}


def test_optional_human_review_does_not_block_automatic_validation() -> None:
    pending = {"pages": 207, "blocks": 673, "formulas": 115, "tables": 29, "figures": 73, "examples": 1}
    report = verification_report("PopGen", {"pages": 207}, pending, [])
    assert report["valid"] is True
    assert report["automated_valid"] is True
    assert report["optional_spot_check_pending"] == pending


def test_automatic_finding_still_blocks_installable_report() -> None:
    report = verification_report("PopGen", {"pages": 207}, {}, ["broken image link"])
    assert report["valid"] is False
    assert report["errors"] == ["broken image link"]


def test_all_baseline_counts_are_gated_including_zero_examples() -> None:
    counts = {"pages": 2, "units": 3, "blocks": 4, "formulas": 5, "logical_tables": 6, "figures": 7, "examples": 0}
    baseline = {"pages": 2, "units": 3, "blocks": 4, "formulas": 5, "tables": 6, "figures": 7, "examples": 0}
    assert expected_count_errors(counts, baseline) == []
    counts["blocks"] = 3
    assert expected_count_errors(counts, baseline) == ["wrong blocks count: 3 != 4"]


def test_formal_examples_and_explicit_absence_rows_have_distinct_counts() -> None:
    assert formal_example_count([{"id": "Example 1", "formal_resource": True}]) == 1
    assert formal_example_count([{"id": "no_formal_examples", "formal_resource": False}]) == 0
    assert formal_example_count([{"id": "no_formal_examples"}]) == 0


def test_status_reports_explicit_waiver_without_claiming_automatic_validity(tmp_path: Path) -> None:
    audit = tmp_path / "audits" / "AnyBook"
    (audit / "reports").mkdir(parents=True)
    (audit / "manifest.json").write_text("{}", encoding="utf-8")
    (audit / "reports" / "verification.json").write_text(
        json.dumps({"automated_valid": False, "errors": ["finding"], "optional_spot_check_pending": {"pages": 1}}), encoding="utf-8"
    )
    (audit / "reports" / "installation.json").write_text(
        json.dumps({"installed": True, "automatic_findings_waived": True, "waived_findings": ["finding"]}), encoding="utf-8"
    )
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "AnyBook.json").write_text("{}", encoding="utf-8")
    result = audit_status("AnyBook", audit_root=tmp_path / "audits", profile_root=profiles)
    assert result["installed"] is True
    assert result["automated_valid"] is False
    assert result["automatic_findings_waived"] is True
    assert result["waived_findings"] == ["finding"]


def test_exact_correction_evidence_and_drift() -> None:
    source = {"master_page": 59, "chapter_page": 1, "bbox": [1.0, 2.0, 3.0, 4.0], "content": "source text"}
    correction = {
        "source_block_id": "p1:b2", "master_page": 59, "chapter_page": 1,
        "bbox": [1, 2, 3, 4], "original": "bad", "replacement": "good",
        "reason": "PDF evidence", "source_content_sha256": hash_bytes(b"source text"),
    }
    assert validate_corrections({"corrections": [correction]}, {"p1:b2": source}) == []
    correction["bbox"] = [1, 2, 3, 5]
    assert "drifted" in validate_corrections({"corrections": [correction]}, {"p1:b2": source})[0]


def test_table_recovery_preserves_all_rows() -> None:
    rows = rows_from_html("<table><tr><td>A</td><td>B</td></tr><tr><td>1</td><td>2</td></tr></table>")
    assert rows == [["A", "B"], ["1", "2"]]


def test_overlap_accepts_union_bbox() -> None:
    assert overlap_ratio([10, 10, 30, 30], [0, 0, 40, 40]) == 1.0


def test_cross_page_provenance_skips_running_header_blocks() -> None:
    ids = ["ch:p1:b7", "ch:p2:b0", "ch:p2:b1", "ch:p2:b2"]
    raw = {
        ids[0]: {"content": "A useful way to think about random drift is to consider subpopulations"},
        ids[1]: {"content": "146"},
        ids[2]: {"content": "CHAPTER 3"},
        ids[3]: {"content": "by drawing alleles at random so each subpopulation remains in equilibrium"},
    }
    delivery = raw[ids[0]]["content"] + " " + raw[ids[3]]["content"]
    selected, score, _ = span_for_content(delivery, ids, raw, 0)
    assert score > 0.9
    assert selected == [ids[0], ids[3]]


def test_persisted_build_findings_survive_later_verify(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "build_findings.json").write_text(
        json.dumps({"findings": ["slice mismatch", "uncovered source"]}), encoding="utf-8"
    )
    assert persisted_build_findings(tmp_path) == ["slice mismatch", "uncovered source"]
    (reports / "build_findings.json").unlink()
    assert persisted_build_findings(tmp_path) == ["persisted build findings are missing"]


def test_uncovered_source_blocks_uses_final_consumed_set() -> None:
    raw = {
        "ch:p001:b1": {"label": "text", "content": "delivered"},
        "ch:p001:b2": {"label": "text", "content": "excluded"},
        "ch:p001:b3": {"label": "text", "content": "missing"},
        "ch:p001:b4": {"label": "header", "content": "not substantive"},
    }
    assert uncovered_source_blocks(
        raw,
        {"ch:p001:b1"},
        {"ch:p001:b2": {"reason": "exact exclusion"}},
    ) == [raw["ch:p001:b3"]]


@pytest.mark.parametrize("label", ["profile", "correction", "ocr", "page", "staging"])
def test_bound_file_drift_is_rejected(tmp_path: Path, label: str) -> None:
    source = tmp_path / f"{label}.json"
    source.write_text("before", encoding="utf-8")
    binding = bind_files([source], tmp_path)
    assert binding_errors(binding, tmp_path, label) == []
    source.write_text("after", encoding="utf-8")
    assert any("drifted" in error for error in binding_errors(binding, tmp_path, label))


def test_artifact_tree_detects_added_and_changed_files(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    binding = bind_tree(tmp_path)
    (tmp_path / "one.txt").write_text("changed", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    errors = tree_binding_errors(binding, tmp_path, "evidence")
    assert any("drifted" in error for error in errors)
    assert any("unexpected" in error for error in errors)


def test_scanned_pages_with_empty_text_layers_are_compared_by_pixels(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    master = tmp_path / "master.pdf"
    chapter = tmp_path / "chapter.pdf"
    for path, color in ((master, (0, 0, 0)), (chapter, (1, 0, 0))):
        document = fitz.open()
        page = document.new_page(width=200, height=200)
        page.draw_rect(fitz.Rect(20, 20, 180, 180), fill=color)
        document.save(path)
        document.close()
    audit = tmp_path / "audit"
    create_tree(audit)
    monkeypatch.setattr(audit_module, "ROOT", tmp_path)
    page_map = [{"master_page": 1, "chapter_page": 1, "slice_pdf": "chapter.pdf"}]
    errors = render_and_compare(master, {}, page_map, audit, 72)
    assert errors
    assert page_map[0]["slice_matches_master"] is False


def test_composite_master_is_built_from_hash_bound_parts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    parts = []
    for index, text in enumerate(("first", "second"), 1):
        path = tmp_path / "data" / f"part{index}.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)
        document = fitz.open()
        page = document.new_page(width=200, height=200)
        page.insert_text((20, 40), text)
        document.save(path)
        document.close()
        parts.append({
            "path": path.relative_to(tmp_path).as_posix(),
            "sha256": audit_module.sha256(path),
            "page_count": 1,
        })
    audit_root = tmp_path / "tmp" / "book_audits"
    monkeypatch.setattr(audit_module, "ROOT", tmp_path)
    monkeypatch.setattr(audit_module, "AUDIT_ROOT", audit_root)
    profile = {
        "book": "Book",
        "master_pdf_glob": "tmp/book_audits/Book/composite/master.pdf",
        "master_pdf_sha256": "0" * 64,
        "master_pdf_parts": parts,
    }
    master = materialize_master(profile)
    with fitz.open(master) as document:
        assert len(document) == 2
        assert "first" in document[0].get_text()
        assert "second" in document[1].get_text()
    parts[0]["sha256"] = "f" * 64
    with pytest.raises(ValueError, match="part hash"):
        materialize_master(profile)


def test_cross_page_evidence_binds_every_source_block_hash() -> None:
    raw = {
        "p1:b1": {"content_sha256": "a"},
        "p2:b1": {"content_sha256": "b"},
    }
    row = {
        "source_pages": [1, 2], "source_block_ids": ["p1:b1", "p2:b1"],
        "source_bboxes": [[1, 2, 3, 4], [5, 6, 7, 8]], "delivery_sha256": "delivery",
    }
    attach_source_hashes(row, raw)
    first = evidence_hash(row, "master", {1: "page1", 2: "page2"})
    row["source_content_sha256"]["p2:b1"] = "changed"
    assert evidence_hash(row, "master", {1: "page1", 2: "page2"}) != first


def test_formula_source_recovery_handles_ocr_suffix_confusion() -> None:
    raw = {
        "ch:p001:b1": {"label": "display_formula", "content": "x=y (20.23\\mathrm{l})", "master_page": 1},
        "ch:p001:b2": {"label": "formula_number", "content": "(20.231)", "master_page": 1},
    }
    ids = {"ch": list(raw)}
    found = resource_source_ids(
        {"id": "20.23l", "label_format": "(20.23l)"}, "formula", "ch", raw, ids,
    )
    assert found == ["ch:p001:b2", "ch:p001:b1"]


def test_unnumbered_formula_recovers_from_exact_master_page_bbox() -> None:
    raw = {
        "ch:p003:b7": {
            "chapter": "ch", "chapter_page": 3, "master_page": 38,
            "label": "display_formula", "content": "x=y", "bbox": [430.0, 650.0, 620.0, 720.0],
        },
    }
    found = resource_source_ids(
        {"id": "formula002", "source": {"page": 38, "bbox": [433.0, 652.0, 618.0, 720.0]}},
        "formula", "ch", raw, {"ch": list(raw)},
    )
    assert found == ["ch:p003:b7"]


def test_master_page_figure_bbox_includes_embedded_panel_labels() -> None:
    raw = {
        "ch:p003:b2": {
            "chapter": "ch", "chapter_page": 3, "master_page": 53,
            "label": "figure_title", "content": "(A)", "bbox": [91.0, 124.0, 126.0, 152.0],
        },
        "ch:p003:b3": {
            "chapter": "ch", "chapter_page": 3, "master_page": 53,
            "label": "image", "content": "", "bbox": [130.0, 125.0, 995.0, 378.0],
        },
    }
    found = resource_source_ids(
        {"id": "3.1", "page": 53, "raw_bbox": [80.0, 120.0, 995.0, 378.0]},
        "figure", "ch", raw, {"ch": list(raw)}, page_mode="master",
    )
    assert found == ["ch:p003:b2", "ch:p003:b3"]


def test_local_example_page_span_resolves_against_master_chapter_range() -> None:
    assert resolve_page_span(8, 9, {"master_start": 201, "master_end": 257}) == (208, 209)
    assert resolve_page_span(124, 125, {"master_start": 123, "master_end": 146}) == (124, 125)


def test_visual_rule_example_boundary_binds_complete_local_page_span() -> None:
    raw = {
        "ch:p008:b1": {"master_page": 208, "content": "before", "bbox": [1, 10, 9, 20]},
        "ch:p008:b2": {"master_page": 208, "content": "Example 8.2.", "bbox": [1, 30, 9, 40]},
        "ch:p008:b3": {"master_page": 208, "content": "worked text", "bbox": [1, 50, 9, 60]},
        "ch:p009:b1": {"master_page": 209, "content": "equation", "bbox": [1, 40, 9, 50]},
        "ch:p009:b2": {"master_page": 209, "content": "after rule", "bbox": [1, 90, 9, 100]},
    }
    item = {
        "label": "Example 8.2", "evidence": {
            "source_page": 8, "visual_stop_clipped": True, "visual_stop_page": 9,
            "visual_stop_rule_bbox": [0, 80, 10, 82],
        },
    }
    found = example_boundary_source_ids(
        item, {"id": "8.2", "source_block_ids": []},
        {"master_start": 201, "master_end": 257}, raw, list(raw),
    )
    assert found == ["ch:p008:b2", "ch:p008:b3", "ch:p009:b1"]


def test_lower_rule_example_boundary_binds_complete_master_page_span() -> None:
    raw = {
        "ch:p002:b1": {"master_page": 124, "content": "Example 3.", "bbox": [1, 30, 9, 40]},
        "ch:p002:b2": {"master_page": 124, "content": "worked text", "bbox": [1, 50, 9, 60]},
        "ch:p003:b1": {"master_page": 125, "content": "equation", "bbox": [1, 40, 9, 50]},
        "ch:p003:b2": {"master_page": 125, "content": "after rule", "bbox": [1, 90, 9, 100]},
    }
    item = {
        "label": "Example 3",
        "evidence": {"source_page": 124, "lower_rule": {"page": 125, "y": 80}},
    }
    found = example_boundary_source_ids(
        item,
        {"id": "3", "source_block_ids": []},
        {"master_start": 123, "master_end": 146},
        raw,
        list(raw),
    )
    assert found == ["ch:p002:b1", "ch:p002:b2", "ch:p003:b1"]


def test_legacy_master_page_block_locator_resolves_exactly() -> None:
    raw = {
        "ch:p003:b6": {"chapter": "ch", "master_page": 38, "chapter_page": 3},
        "ch:p004:b6": {"chapter": "ch", "master_page": 39, "chapter_page": 4},
    }
    assert explicit_source_ids("ch", ["p38:b6"], raw, {"ch": list(raw)}) == ["ch:p003:b6"]
    assert explicit_source_ids("ch", ["p4:b6"], raw, {"ch": list(raw)}) == ["ch:p004:b6"]


def test_source_exclusion_requires_exact_id_bbox_reason_and_content_hash() -> None:
    raw = {"ch:p1:b1": {"bbox": [1.0, 2.0, 3.0, 4.0], "content_sha256": "hash"}}
    profile = {"source_block_exclusions": [{
        "source_block_id": "ch:p1:b1", "bbox": [1.0, 2.0, 3.0, 4.0],
        "reason": "running header", "source_content_sha256": "hash",
    }]}
    errors: list[str] = []
    assert set(source_exclusions(profile, raw, errors)) == {"ch:p1:b1"}
    assert errors == []
    profile["source_block_exclusions"][0]["bbox"] = [1.0, 2.0, 3.0, 5.0]
    assert source_exclusions(profile, raw, errors) == {}


def test_source_coverage_provenance_attachment_is_idempotent() -> None:
    target = {
        "source_page": 10,
        "source_pages": [10],
        "source_block_ids": ["ch:p010:b1"],
        "source_bboxes": [[1, 2, 3, 4]],
    }
    row = {
        "source_block_id": "ch:p011:b2",
        "master_page": 11,
        "bbox": [5, 6, 7, 8],
    }
    append_provenance(target, row)
    append_provenance(target, row)
    assert target["source_block_ids"] == ["ch:p010:b1", "ch:p011:b2"]
    assert target["source_pages"] == [10, 11]
    assert target["source_bboxes"] == [[1, 2, 3, 4], [5, 6, 7, 8]]


def test_installed_delivery_binding_detects_owned_file_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    owned = tmp_path / "data" / "structured" / "Book_chapter1_001.json"
    owned.parent.mkdir(parents=True)
    owned.write_text("original", encoding="utf-8")
    audit = tmp_path / "tmp" / "book_audits" / "Book"
    reports = audit / "reports"
    reports.mkdir(parents=True)
    monkeypatch.setattr(audit_module, "ROOT", tmp_path)
    reports.joinpath("installation.json").write_text(json.dumps({
        "installed": True,
        "delivery": book_delivery_binding("Book", root=tmp_path),
    }), encoding="utf-8")
    assert installed_delivery_errors("Book", audit) == []
    owned.write_text("drift", encoding="utf-8")
    assert installed_delivery_errors("Book", audit) == [
        "installed Book delivery differs from the transaction report"
    ]


def test_install_failure_restores_original_book_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = tmp_path / "data" / "structured"
    data.mkdir(parents=True)
    original = data / "Book_chapter1_001.json"
    original.write_text("original", encoding="utf-8")
    audit_root = tmp_path / "tmp" / "book_audits"
    staged = audit_root / "Book" / "staging" / "data" / "structured"
    staged.mkdir(parents=True)
    (staged / original.name).write_text("replacement", encoding="utf-8")
    reports = audit_root / "Book" / "reports"
    reports.mkdir(parents=True)
    (reports / "protected_hashes.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(audit_module, "ROOT", tmp_path)
    monkeypatch.setattr(audit_module, "AUDIT_ROOT", audit_root)
    monkeypatch.setattr(audit_module, "verify", lambda _book, **_kwargs: {"valid": True})
    monkeypatch.setattr(audit_module, "protected_hashes", lambda _book: {})
    monkeypatch.setattr(audit_module.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError("injected")))
    with pytest.raises(RuntimeError, match="rolled back"):
        install("Book")
    assert original.read_text(encoding="utf-8") == "original"
