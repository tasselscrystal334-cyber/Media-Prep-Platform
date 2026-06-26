from pathlib import Path

from mediaqc.hash_check import calculate_sha256


def test_calculate_sha256_streaming(tmp_path: Path) -> None:
    path = tmp_path / "中文 file.mov"
    path.write_bytes(b"abc")

    assert calculate_sha256(path) == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )
