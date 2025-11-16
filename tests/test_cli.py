from pathlib import Path

import pytest

from traffic_counter.cli import main


def test_cli_outputs_expected_sections(tmp_path, capsys):
    """
    测试 CLI 输出包含预期的所有部分
    
    测试要点：
    - 使用 pytest 的 tmp_path fixture 创建临时文件。
      如果不用 fixture，需要手动创建和清理文件，代码冗长且容易出错
    - 使用 capsys fixture 捕获标准输出和标准错误。
      如果不用 capsys，无法验证 CLI 的输出内容
    - 验证输出格式和内容是否正确。
      如果不对输出进行验证，无法确保 CLI 功能正常
    """
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

    exit_code = main([str(sample), "--window", "2", "--top", "2"])
    assert exit_code == 0
    
    captured = capsys.readouterr().out.splitlines()

    assert captured[0] == "Total 31"
    assert captured[1] == "2021-12-01 31"
    assert captured[2] == "Top half hours:"
    assert "Lowest traffic window:" in captured


def test_cli_file_not_found(capsys):
    """
    测试文件不存在时的错误处理
    
    测试要点：
    - 验证文件不存在时返回正确的退出码（非零）。
      如果退出码不正确，调用者无法判断程序是否失败
    - 验证错误信息输出到标准错误流。
      如果错误信息输出到标准输出，无法区分正常输出和错误信息
    - 验证错误信息包含文件名。
      如果错误信息不包含文件名，用户无法知道哪个文件出错
    """
    exit_code = main(["nonexistent_file.txt"])
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err
    assert "nonexistent_file.txt" in captured.err

