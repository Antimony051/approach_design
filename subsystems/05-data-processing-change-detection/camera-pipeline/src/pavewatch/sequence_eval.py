"""Common pass-local, class-specific object matching for all three replays."""

from collections import Counter

from . import CLASSES
from .sequence_geometry import iou


def validate_labels(doc, session, frames):
    if doc["pass_id"] != session["pass_id"] or doc["site_id"] != session["site_id"]:
        raise ValueError("Annotation site/pass differs from session")
    sizes = {f.id: (f.width, f.height) for f in frames}
    ids = set()
    for r in doc["objects"] + doc["nuisances"]:
        if r["id"] in ids or not r["views"]:
            raise ValueError("Duplicate or unlocated annotation")
        ids.add(r["id"])
        for frame, box in r["views"].items():
            w, h = sizes[frame]
            if not (len(box) == 4 and 0 <= box[0] < box[2] <= w and 0 <= box[1] < box[3] <= h):
                raise ValueError(f"Invalid reference region {r['id']} {frame}")
    if any(r["class_name"] not in CLASSES for r in doc["objects"]):
        raise ValueError("Unknown annotation class")


def overlap(views, target, t):
    return [
        (v["frame_id"], iou(v["box"], target["views"][v["frame_id"]]))
        for v in views
        if v["frame_id"] in target["views"] and iou(v["box"], target["views"][v["frame_id"]]) >= t
    ]


def match(edges):
    # Maximum cardinality; high-overlap alternatives are visited first.
    owner = {}

    def assign(alert, seen):
        for idx, _ in edges[alert]:
            if idx in seen:
                continue
            seen.add(idx)
            if idx not in owner or assign(owner[idx], seen):
                owner[idx] = alert
                return True
        return False

    for i in sorted(range(len(edges)), key=lambda i: len(edges[i])):
        assign(i, set())
    return set(owner.values())


def evaluate(findings, proposals, tracks, frames, truth, session, cfg, seconds):
    limit = cfg["evaluation_box_iou"]
    results = {}
    for ch, name in enumerate(CLASSES):
        gt = [o for o in truth["objects"] if o["class_name"] == name]

        def locations(regions, channel=ch):
            return [
                {"frame_id": frames[r.frame].id, "box": r.box}
                for r in regions
                if r.channel == channel
            ]

        raw = locations(r for rows in proposals for r in rows)
        tracks_by_frame = [locations(t.sightings) for t in tracks if t.sightings[0].channel == ch]
        alerts = [f for f in findings if f["class_name"] == name]
        views = [[e for e in f["evidence"] if e["used_for_decision"]] for f in alerts]
        edges = []
        for group in views:
            scores = [
                (j, max((s for _, s in overlap(group, g, limit)), default=0))
                for j, g in enumerate(gt)
            ]
            edges.append(sorted([(j, s) for j, s in scores if s > 0], key=lambda v: -v[1]))
        matched = match(edges)
        tp, fp = len(matched), len(views) - len(matched)
        nuisance = Counter()
        for i, group in enumerate(views):
            if i not in matched:
                for kind in {n["kind"] for n in truth["nuisances"] if overlap(group, n, limit)}:
                    nuisance[kind] += 1
        proposed = sum(bool(overlap(raw, g, limit)) for g in gt)
        linked = sum(
            any(
                len({f for f, _ in overlap(group, g, limit)}) >= 2
                for group in tracks_by_frame + views
            )
            for g in gt
        )
        distance = session.get("measured_path_m")
        results[name] = {
            "tp": tp,
            "fp": fp,
            "fn": len(gt) - tp,
            "precision": tp / len(alerts) if alerts else None,
            "recall": tp / len(gt) if gt else None,
            "duplicate_alerts": sum(bool(edges[i]) for i in range(len(edges)) if i not in matched),
            "proposed": proposed,
            "linked": linked,
            "positive_objects": len(gt),
            "proposal_recall": proposed / len(gt) if gt else None,
            "linked_fraction": linked / len(gt) if gt else None,
            "false_findings_per_100m": 100 * fp / distance if distance else None,
            "nuisance_errors": dict(nuisance),
        }
    return {
        "classes": results,
        "seconds": seconds,
        "seconds_per_100_frames": 100 * seconds / len(frames),
    }


def markdown(report):
    lines = [
        "# Sequence replay",
        "",
        f"Pass `{report['pass_id']}` · {report['frames']} exposures · {report['capture_profile']}",
        "",
        f"Model `{report['model_version']}` · configuration `{report['config_sha256'][:12]}`",
        "",
        "| Run | Class | TP | FP | FN | Precision | Recall | Duplicates | Proposed / linked / labeled | FP / 100 m | Seconds / 100 frames |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    def val(n):
        return "—" if n is None else f"{n:.3f}"

    for mode, stats in report["metrics"].items():
        for name, c in stats["classes"].items():
            lines.append(
                f"| {mode} | {name} | {c['tp']} | {c['fp']} | {c['fn']} | {val(c['precision'])} | {val(c['recall'])} | {c['duplicate_alerts']} | {c['proposed']} / {c['linked']} / {c['positive_objects']} | {val(c['false_findings_per_100m'])} | {stats['seconds_per_100_frames']:.2f} |"
            )
    lines.extend(
        [
            "",
            "A uses v0 whole-frame scores. B adds independent original-image crops. C applies the separated-view rule to registered crops. A and B collate accepted sightings for counting only.",
            "",
            "Timings include shared input checks and the stages required for each variant in this replay. Model loading, scoring the annotations and writing JSON are excluded. A dash denotes an unavailable denominator.",
            "",
            "Source pixel rectangles use half-open [left, top, right, bottom] coordinates after EXIF orientation. The JSON includes masks, evidence, registrations and nuisance counts. Synthetic translations test the pipeline mechanics. Field evaluation requires independently labeled sites and measured passes.",
        ]
    )
    return "\n".join(lines) + "\n"
