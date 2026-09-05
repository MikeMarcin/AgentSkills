#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


STUDIO_APP = Path("/Applications/InstaMAT Studio.app")
STUDIO_ENVIRONMENT = STUDIO_APP / "Contents/Resources/Environment"
PIPELINE_CANDIDATES = (
    Path("/Applications/InstaMAT Pipeline.app/Contents/MacOS/InstaMATPipeline"),
    Path("/Applications/InstaMAT Pipeline/InstaMATPipeline"),
    Path.home() / "Applications/InstaMAT Pipeline.app/Contents/MacOS/InstaMATPipeline",
    Path.home() / "Applications/InstaMAT Pipeline/InstaMATPipeline",
)
MATERIAL_OUTPUT_FILTER = "*BaseColor*;*Normal*;*Roughness*;*Metalness*;*AmbientOcclusion*;*Height*"
OFFICIAL_PIPELINE_DOCS = "https://docs.instamat.io/en/Products/InstaMAT_Pipeline"


def _sha256(aPath: Path) -> str:
    digest = hashlib.sha256()
    with aPath.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _pipeline_candidates(aExplicit: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if aExplicit is not None:
        candidates.append(aExplicit.expanduser())
    if configured := os.environ.get("INSTAMAT_PIPELINE"):
        candidates.append(Path(configured).expanduser())
    if discovered := shutil.which("InstaMATPipeline"):
        candidates.append(Path(discovered))
    candidates.extend(PIPELINE_CANDIDATES)
    return candidates


def _find_pipeline(aExplicit: Path | None) -> Path | None:
    for candidate in _pipeline_candidates(aExplicit):
        resolved = candidate.resolve()
        if resolved.is_file() and os.access(resolved, os.X_OK):
            return resolved
    return None


def _require_pipeline(aExplicit: Path | None) -> Path:
    pipeline = _find_pipeline(aExplicit)
    if pipeline is None:
        raise RuntimeError(
            "InstaMATPipeline was not found. InstaMAT Studio is the GUI authoring app; "
            "documented CLI execution requires the separately downloaded InstaMAT Pipeline product. "
            f"See {OFFICIAL_PIPELINE_DOCS}"
        )
    return pipeline


def _environment(aExplicit: Path | None) -> Path | None:
    if aExplicit is not None:
        environment = aExplicit.expanduser().resolve()
        if not environment.is_dir():
            raise RuntimeError(f"InstaMAT environment not found: {environment}")
        return environment
    return STUDIO_ENVIRONMENT.resolve() if STUDIO_ENVIRONMENT.is_dir() else None


def _command_prefix(
    aPipeline: Path,
    aMode: str,
    aPackage: Path | None,
    aEnvironment: Path | None,
) -> list[str]:
    command = [str(aPipeline)]
    if environment := _environment(aEnvironment):
        command.extend(("-env", str(environment)))
    command.extend(("-mode", aMode))
    if aPackage is not None:
        package = aPackage.expanduser().resolve()
        if not package.is_file():
            raise RuntimeError(f"InstaMAT package not found: {package}")
        command.append(str(package))
    return command


def _parse_parameter(aValue: str) -> tuple[str, str]:
    name, separator, value = aValue.partition("=")
    if not separator or not name or not value:
        raise argparse.ArgumentTypeError("parameter must be NAME=JSON")
    try:
        json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"parameter value is not JSON: {exc}") from exc
    return name, value


def _append_parameter(aCommand: list[str], aName: str, aValue: Any) -> None:
    aCommand.extend(("-parameter", aName, json.dumps(aValue, separators=(",", ":"))))


def _doctor(aArgs: argparse.Namespace) -> int:
    pipeline = _find_pipeline(aArgs.pipeline)
    report = {
        "studio_app": str(STUDIO_APP),
        "studio_installed": STUDIO_APP.is_dir(),
        "pipeline": str(pipeline) if pipeline is not None else None,
        "pipeline_ready": pipeline is not None,
        "studio_environment": str(STUDIO_ENVIRONMENT),
        "studio_environment_ready": STUDIO_ENVIRONMENT.is_dir(),
        "official_pipeline_docs": OFFICIAL_PIPELINE_DOCS,
        "note": (
            "Ready for documented headless graph execution."
            if pipeline is not None
            else "Install InstaMAT Pipeline from the license portal; Studio alone is not the documented CLI renderer."
        ),
    }
    print(json.dumps(report, indent=2))
    return 0


def _info(aArgs: argparse.Namespace) -> int:
    pipeline = _require_pipeline(aArgs.pipeline)
    command = _command_prefix(pipeline, "Info", aArgs.package, aArgs.environment)
    command.extend(("-graphInfo", aArgs.graph))
    return subprocess.run(command, check=False).returncode


def _materialize_command(aArgs: argparse.Namespace, aPipeline: Path) -> tuple[list[str], Path, Path]:
    source = aArgs.input.expanduser().resolve()
    if not source.is_file():
        raise RuntimeError(f"Input image not found: {source}")
    output = aArgs.output.expanduser().resolve()
    command = _command_prefix(aPipeline, "Execute", aArgs.package, aArgs.environment)
    command.extend(("-graph", aArgs.graph, str(aArgs.resolution), str(aArgs.resolution)))
    _append_parameter(command, "Input", source.as_uri())
    _append_parameter(command, "SharpenInput", aArgs.sharpen)
    _append_parameter(command, "StrengthBaseColorShadowCancellation", aArgs.shadow_cancellation)
    _append_parameter(command, "SharpnessBaseColorShadowCancellation", aArgs.shadow_sharpness)
    _append_parameter(command, "Normal", aArgs.normal)
    _append_parameter(command, "StrengthNormal", aArgs.normal_strength)
    _append_parameter(command, "Height", aArgs.height)
    _append_parameter(command, "AmbientOcclusion", aArgs.ambient_occlusion)
    _append_parameter(command, "Metalness", aArgs.metalness)
    for name, value in aArgs.parameter:
        command.extend(("-parameter", name, value))
    command.extend(("-executionType", aArgs.execution_type))
    command.extend(("-outputFilter", MATERIAL_OUTPUT_FILTER))
    command.extend(("-outputPathFormat", str(output / f"{{OUTPUT.NAME}}.{aArgs.output_format}")))
    if aArgs.software:
        command.insert(1, "-software")
    return command, source, output


def _materialize(aArgs: argparse.Namespace) -> int:
    pipeline = _find_pipeline(aArgs.pipeline)
    if pipeline is None:
        if not aArgs.dry_run:
            pipeline = _require_pipeline(aArgs.pipeline)
        else:
            pipeline = Path(aArgs.pipeline or "InstaMATPipeline")
    command, source, output = _materialize_command(aArgs, pipeline)
    preview = {
        "pipeline": str(pipeline),
        "command": command,
        "input": str(source),
        "output": str(output),
        "dry_run": aArgs.dry_run,
    }
    if aArgs.dry_run:
        print(json.dumps(preview, indent=2))
        return 0

    output.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"InstaMAT Pipeline exited with status {completed.returncode}")
    textures = sorted(
        path
        for path in output.iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".png8", ".png16", ".exr", ".tif", ".tiff"}
    )
    if not textures:
        raise RuntimeError("InstaMAT Pipeline completed without producing any texture files")
    record = {
        "schema": "instamat.image_to_pbr.v1",
        "status": "review_candidate",
        "pipeline": str(pipeline),
        "graph": aArgs.graph,
        "package": str(aArgs.package.expanduser().resolve()) if aArgs.package else None,
        "command": command,
        "input": {"path": str(source), "sha256": _sha256(source)},
        "resolution": aArgs.resolution,
        "execution_type": aArgs.execution_type,
        "outputs": [
            {"path": str(path), "sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in textures
        ],
        "promotion_policy": "requires_visual_review_and_explicit_project_approval",
    }
    record_path = output / "instamat-materialize-run.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0


def _add_pipeline_argument(aParser: argparse.ArgumentParser) -> None:
    aParser.add_argument("--pipeline", type=Path, help="Explicit InstaMATPipeline executable")
    aParser.add_argument("--environment", type=Path, help="InstaMAT package environment; defaults to Studio's Environment directory")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate review-only PBR texture maps with InstaMAT Pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Report Studio and Pipeline availability")
    _add_pipeline_argument(doctor)
    doctor.set_defaults(handler=_doctor)

    info = subparsers.add_parser("info", help="Print the installed Materialize Image graph surface")
    _add_pipeline_argument(info)
    info.add_argument("--package", type=Path)
    info.add_argument("--graph", default="Materialize Image")
    info.set_defaults(handler=_info)

    materialize = subparsers.add_parser("materialize", help="Generate a PBR texture candidate set")
    _add_pipeline_argument(materialize)
    materialize.add_argument("input", type=Path)
    materialize.add_argument("output", type=Path)
    materialize.add_argument("--package", type=Path)
    materialize.add_argument("--graph", default="Materialize Image")
    materialize.add_argument("--resolution", type=int, choices=(512, 1024, 2048, 4096), default=2048)
    materialize.add_argument("--execution-type", choices=("Normalized8", "Normalized16", "FullRange16", "FullRange32"), default="Normalized16")
    materialize.add_argument("--output-format", choices=("png8", "png16"), default="png16")
    materialize.add_argument("--sharpen", type=float, default=0.0)
    materialize.add_argument("--shadow-cancellation", type=float, default=0.8)
    materialize.add_argument("--shadow-sharpness", type=float, default=0.5)
    materialize.add_argument("--normal", action=argparse.BooleanOptionalAction, default=True)
    materialize.add_argument("--normal-strength", type=float, default=1.0)
    materialize.add_argument("--height", action=argparse.BooleanOptionalAction, default=True)
    materialize.add_argument("--ambient-occlusion", action=argparse.BooleanOptionalAction, default=True)
    materialize.add_argument("--metalness", action=argparse.BooleanOptionalAction, default=False)
    materialize.add_argument("--parameter", action="append", type=_parse_parameter, default=[])
    materialize.add_argument("--software", action="store_true", help="Use Pipeline's CPU execution backend")
    materialize.add_argument("--dry-run", action="store_true")
    materialize.set_defaults(handler=_materialize)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
