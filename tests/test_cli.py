from pathlib import Path

from traffic_counter.cli import main


def test_cli_outputs_expected_sections(tmp_path, capsys):
    sample = tmp_path / "sample.txt"
    sample.write_text(
        "\n".join(
            [
                "2021-12-01T05:00:00 5",
                "2021-12-01T05:30:00 12",
                "2021-12-01T06:00:00 14",
            ]
        ),
        encoding="utf-8",
    )

    main([str(sample), "--window", "2", "--top", "2"])
    captured = capsys.readouterr().out.splitlines()

    assert captured[0] == "Total 31"
    assert captured[1] == "2021-12-01 31"
    assert captured[2] == "Top half hours:"
    assert "Lowest traffic window:" in captured

