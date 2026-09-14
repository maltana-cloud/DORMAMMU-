from devintel.modules.engineering import EngineeringIntelligence


def test_analyzer_is_deterministic_and_reports_imports():
    files = {"a.py": "import b\nvalue = 1\n", "b.py": "value = 2\n"}
    first = EngineeringIntelligence().analyze("scope", files)
    second = EngineeringIntelligence().analyze("scope", files)
    assert first == second
    assert first.safe
    assert first.source_digest
    assert ("a.py", ("b",)) in first.imports


def test_dynamic_execution_is_flagged_without_execution():
    report = EngineeringIntelligence().analyze("scope", {"unsafe.py": "eval('1+1')\nexec('x=1')\n"})
    assert not report.safe
    assert {f.kind for f in report.findings} == {"dynamic_execution"}


def test_syntax_errors_are_evidence_not_executed_code():
    report = EngineeringIntelligence().analyze("scope", {"broken.py": "def broken(:\n"})
    assert not report.safe
    assert any(f.kind == "syntax" for f in report.findings)


def test_file_and_source_bounds_fail_closed():
    analyzer = EngineeringIntelligence()
    try:
        analyzer.analyze("scope", {f"{i}.py": "" for i in range(129)})
    except ValueError:
        pass
    else:
        raise AssertionError("file bound was not enforced")
    report = analyzer.analyze("scope", {"huge.py": "x" * 200001})
    assert not report.safe
    assert report.findings[0].kind == "bound"
