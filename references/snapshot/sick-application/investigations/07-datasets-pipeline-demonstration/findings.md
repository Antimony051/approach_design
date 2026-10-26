# Datasets and pre-hardware pipeline demonstration

## 1. Scope and recommendation

### Recommendation

Use a three-part, laptop-scale data package for the pre-hardware demonstration:

1. **UAV-PDD2023 for aerial RGB relevance and adapter testing.** It is the best primary image dataset found for PaveWatch because it contains 2,440 downward-looking UAV images acquired at a reported 30 m altitude, 11,158 PASCAL VOC bounding-box annotations, six pavement-distress classes, and an explicit CC BY 4.0 license. It is much closer to PaveWatch's proposed camera viewpoint than a dashboard-camera dataset.
2. **Rui Fan's Stereo Pothole Datasets for the controlled image-only versus image-plus-geometry comparison.** The repository contains 67 aligned RGB, disparity, point-cloud, and pixel-label samples under an MIT license. It is small enough for CPU experiments and is the clearest legally reusable paired RGB/geometry source found. It is a ground-vehicle stereo dataset rather than UAV or picoScan150 data, so it can validate the software interface and experimental method only.
3. **A deterministic analytic surface generator for baseline-versus-current geometric change.** Generate known heave, settlement, rut, pothole-like depression, and edge-drop fixtures; sample them as moving 2D profiles; then add configurable noise, pose error, dropout, and alignment error. This gives exact ground truth for change magnitude and location without implying that the generator reproduces picoScan150 physics.

The smallest credible demonstration should produce two results:

- a **geometric-change result** from synthetic baseline/current survey profiles; and
- a **paired fusion result** comparing the same simple classifier using RGB features alone and RGB plus registered depth/shape features on the Stereo Pothole data.

UAV-PDD2023 should also be ingested, audited, split without near-duplicate leakage, and displayed with ground-truth boxes. Training a full aerial object detector is a useful enhancement, but it is not required to prove the pre-hardware data pipeline on an ordinary laptop.

RDD2022 is the preferred fallback for aerial or road-scene RGB data. Its China Drone subset is only about 153 MB and its United States subset is about 424 MB, avoiding the complete 12.36 GB archive. SDNET2018 is a second image fallback for binary crack/non-crack classification.

### Claims this work can and cannot support

This investigation is **proposed research and a planned software demonstration**. No dataset has been downloaded into the repository, no experiment has been run, and no performance has been measured by the PaveWatch team.

The eventual demonstration may show that adapters, provenance, change differencing, evaluation, and reporting work on public or simulated inputs. It cannot establish:

- picoScan150 range accuracy, pavement sampling density, or minimum detectable deformation;
- UAV vibration, timing, calibration, localization, or repeat-flight performance;
- improvement on PaveWatch UAV imagery from adding picoScan150 data;
- field performance on Mississippi pavement; or
- safety, accessibility, or maintenance suitability.

Those claims require controlled data from the team's actual camera, aircraft, positioning system, and supplied picoScan150.

## 2. Evidence and assumptions

### Status of evidence

| Status | What it means here |
|---|---|
| **Proposed** | Dataset and method selected by this investigation, subject to integration decisions. |
| **Available** | Publicly hosted by the cited maintainer at the access date; not present locally. |
| **Planned** | Work to implement after this brief. |
| **Simulated** | Data that will be generated from declared equations and parameters. |
| **Measured** | None. The repository contains no PaveWatch dataset or experimental result. |

### Ranked dataset assessment

Licenses below are the terms displayed by the maintainer or repository on **2026-09-19**. Preserve a copy of the applicable license and metadata with every downloaded version. “Competition use” means a noncommercial university demonstration; it does not remove attribution, share-alike, or noncommercial conditions.

| Rank | Dataset and intended use | Modality, labels, size, and domain | License and access | Assessment for PaveWatch |
|---:|---|---|---|---|
| 1 | [**UAV-PDD2023**](https://doi.org/10.5281/zenodo.8429208) — primary aerial RGB source | 2,440 RGB images at 2,592 × 1,944; 11,158 PASCAL VOC boxes for longitudinal, transverse, alligator, and oblique cracks, repair, and potholes. Images were collected in China with a downward UAV camera at 30 m over highway, provincial, and county roads in clear and post-rain conditions. The archive is 2.1 GB with a published MD5. | [**CC BY 4.0**](https://creativecommons.org/licenses/by/4.0/legalcode). Direct download, no account reported. Commercial and competition use are permitted with attribution. | Best viewpoint match and an explicit license. Boxes locate defects but do not provide crack contours, severity, metric dimensions, depth, pose, repeat surveys, or Mississippi-domain evidence. Mirroring/augmentation occurred during dataset construction, so perceptual duplicate grouping must precede any new split. |
| 2 | [**Stereo Pothole Datasets**](https://github.com/ruirangerfan/stereo_pothole_datasets) — paired RGB/geometry fusion smoke test | 67 frames across three dataset folders (22, 40, and 5). Each frame has aligned RGB, disparity, transformed disparity, 3D point cloud, and pixel-level pothole label. A sampled RGB file is 1,730 × 1,028; the repository is approximately 3.2 GiB. Capture geography and weather are not documented in the repository. | Repository-wide [**MIT License**](https://github.com/ruirangerfan/stereo_pothole_datasets/blob/master/LICENSE). Direct Git access. Commercial and competition use are permitted with copyright/license preservation. | Only candidate found that is small, paired, labeled, and permissively licensed. Excellent for testing whether depth features add value on the same examples. It is stereo/ground-vehicle data, contains only potholes, has only 67 frames, and is not a temporal change dataset. The authors list 12 Dataset 2 frame results as unused for evaluation; their treatment must be recorded before benchmarking. |
| 3 | [**RDD2022**](https://doi.org/10.6084/m9.figshare.21431547) — fallback and cross-domain RGB test | 47,420 road images from Japan, India, Czech Republic, Norway, the United States, and China; more than 55,000 boxes for longitudinal, transverse, and alligator cracks and potholes. Resolutions span 512 × 512 to 3,650 × 2,044. Modalities include vehicle, motorbike, high-resolution road, Street View, and a China Drone subset. Complete archive: 12.36 GB; country archives are available separately. | Figshare says [**CC BY 4.0**](https://creativecommons.org/licenses/by/4.0/legalcode); the maintainers' [GitHub README](https://github.com/sekilab/RoadDamageDetector#license) says [**CC BY-SA 4.0**](https://creativecommons.org/licenses/by-sa/4.0/legalcode) for images. Both permit commercial and competition use with conditions, but the conflict must be resolved for the exact downloaded files; conservatively treat derivatives as CC BY-SA until then. | Strong diversity and a small drone subset. Useful for transfer testing, but most views differ from PaveWatch, labels are boxes only, there is no matched depth or temporal baseline, and source-specific duplicates may exist. Do not redistribute a repackaged subset until the license discrepancy is documented. |
| 4 | [**SDNET2018**](https://doi.org/10.15142/T3TD19) — compact crack-classification fallback | 56,000+ 256 × 256 tiles of cracked and uncracked concrete bridge decks, walls, and pavement. Source photographs came from a 16 MP Nikon camera; 104 source pavement photographs were tiled. Includes shadows, debris, edges, holes, surface texture, and cracks reported from 0.06 to 25 mm. The archive is about 504 MB. Labels are binary at tile level, not pixel masks. | [**CC BY 4.0**](https://creativecommons.org/licenses/by/4.0/legalcode). Direct download. Commercial and competition use are permitted with attribution. | Legally clean, small, and useful for an image-loader/classification fallback. The many tiles come from only 230 source photos across all structural types, so random tile splitting would leak nearly identical content. Concrete close-ups and binary labels are a large domain mismatch for aerial asphalt surveys. |
| 5 | [**RSRD**](https://thu-rsxd.com/rsrd/) — optional road-surface reconstruction reference | 2,800 paired samples with dense labels and 13,000 with sparse labels: rectified stereo RGB, LiDAR point clouds, depth/disparity, pose/location, plus short continuous sequences. Captured from a road vehicle in Qingdao, China on concrete and asphalt in sunny conditions. Maintainer reports 5 Hz sensing and 2,500/300 dense train/test division. It has surface geometry but not PaveWatch distress/change labels. | The [maintainer site](https://thu-rsxd.com/) states **CC BY-NC** and academic research only; access is through linked Figshare records. Competition research may fit, but commercial use is prohibited. The development kit is MIT; that does not change the dataset license. | Much larger and richer than needed for the first demo and useful later for reconstruction research. Noncommercial terms conflict with PaveWatch's commercialization path, so do not train a product-bound model on it. It is not a picoScan150 or aerial dataset. |
| 6 | [**USGS 3DEP**](https://www.usgs.gov/3d-elevation-program) — optional open point-cloud parser fixture | Airborne LiDAR point clouds/DEMs across the United States, distributed in LAS/LAZ and cloud forms. No pavement-distress labels, RGB pairing, or guaranteed repeat survey of a chosen paved site. USGS describes general lidar vertical accuracy on the order of 10 cm, which is too coarse for the intended small pavement changes. | U.S. Government **public domain**; free of charge and without use restrictions. Direct National Map/AWS access; cloud use may have transfer/requester costs. | Legally excellent for testing LAS/LAZ ingestion, coordinate reference systems, and large-point-cloud handling. It is not suitable ground truth for crack, rut, or small heave detection and should not be presented as such. |
| 7 | [**PaveSeg preview**](https://github.com/FuturePave/PaveSeg-Dataset) — segmentation alternative requiring license review | Repository describes 2,400 images at 1,280 × 1,080 with pixel masks for seven pavement categories; only a 100-image preview is currently available. Full access is described as noncommercial and through a request process that the README says is still forthcoming. | GitHub has an [**Apache-2.0**](https://github.com/FuturePave/PaveSeg-Dataset/blob/main/LICENSE) file, while the README separately restricts full-data access to noncommercial use. | Pixel masks are attractive, but access and data-license terms are not sufficiently clear for the primary plan. Use only after written terms for the exact data files are unambiguous. |
| 8 | [**UAPD**](https://github.com/tantantetetao/UAPD-Pavement-Distress-Dataset) — UAV alternative requiring a real license | Repository states 3,151 UAV pavement-distress images across six classes and links a Google Drive archive. It describes the data as released for “public use” but provides no recognized license file or detailed reuse terms. | No explicit dataset license found. Competition and commercial permission are therefore **unknown**. | Viewpoint is relevant, but “public use” is not a complete reuse license. Do not download for the application demo unless the maintainer publishes clear terms. |
| 9 | [**KITTI**](https://www.cvlibs.net/datasets/kitti/) — generic multimodal fallback of last resort | Vehicle RGB, stereo, Velodyne scans, calibration, and road-driving data from Germany; established tasks and devkits, but no pavement-distress/change labels and low road-surface emphasis. | [**CC BY-NC-SA 3.0**](https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode); noncommercial and share-alike. | Can test generic synchronized camera/LiDAR parsing but contributes little to the pavement objective. RSRD and the Stereo Pothole data are more relevant. |

### Recommended pairing and domain mismatch

The best open **application-facing pair** is UAV-PDD2023 plus the analytic synthetic profiles:

- UAV-PDD2023 exercises high-resolution, downward-looking RGB ingestion and defect labels.
- Synthetic profiles exercise repeat-survey geometry with exactly known changes.

They are intentionally not treated as a naturally paired sensor dataset. The RGB boxes and synthetic height fields must never be combined into a claimed physical measurement.

The Stereo Pothole dataset fills a narrower experimental gap: it allows a fair image-only versus image-plus-geometry comparison on aligned samples. Its result answers “does this fusion code and evaluation design run?” It does not answer “will picoScan150 improve aerial crack detection?”

Important mismatches to validate later include sensor physics, scan orientation, flight altitude, ground sampling distance, asphalt and concrete appearance in Mississippi, shadows and wetness, defect size distribution, pose/timestamp errors, and the absence of true repeat surveys in every recommended public dataset.

## 3. Proposed components or software

### Reproducible software environment

Implement the demo as a small Python project managed by `uv`, with a committed lockfile. A practical CPU stack is:

- Python, standard-library XML/JSON/CSV readers, and `hashlib` for manifests and checksums;
- NumPy and SciPy for surfaces, fitting, filtering, and metrics;
- OpenCV for image decoding, gradients, resizing, masks, and perceptual duplicate checks;
- scikit-learn for a transparent logistic-regression or shallow tree baseline;
- pandas plus Parquet support for tables; and
- Matplotlib for fixed, exportable plots.

Pin exact versions when implementation starts and record the Python version, operating system, dependency lock hash, Git commit, dataset DOI/version, archive checksum, configuration hash, and random seed in every run manifest. A deep-learning framework is optional and should not be a dependency of the minimum demonstration.

### Synthetic surface fixture

Use a local survey frame in meters with a deterministic baseline surface:

```text
z_baseline(x, y) = cross_slope(y) + crown(y) + low_frequency_texture(x, y)
```

Construct `z_current` by adding parameterized fixtures with stored ground truth:

- Gaussian or flat-topped positive bump for heave;
- negative Gaussian/bowl for settlement;
- two elongated wheel-path depressions for rutting;
- compact depression with a steeper rim for a pothole-like feature; and
- a step or tapered discontinuity for an edge drop.

The default fixture should cover a modest virtual area, such as 20 m × 4 m. Grid resolution, scan spacing, noise, and anomaly dimensions must be configuration values rather than claims about the sensor. Investigation 02 must later supply plausible picoScan150 scan parameters.

Generate a sequence of platform poses and intersect a generic 2D scan plane with the analytic surface, or initially sample the surface along moving transverse profiles. Export range/profile samples with exact pose and time. Optional perturbations should be independently switchable:

- range noise and bias;
- roll/pitch/height error;
- timestamp/along-track displacement;
- missing returns and isolated outliers;
- reduced coverage; and
- baseline/current XY and yaw offsets.

Name this component a **generic profile fixture**, not a picoScan150 simulator. It omits beam shape, reflectivity, multipath, internal filtering, real IMU behavior, and firmware timing.

## 4. Interfaces and data flow

### Demonstration flow

```text
License/checksum manifest
        |
        +--> UAV-PDD2023 adapter --> normalized RGB records + VOC boxes --> aerial audit
        |
        +--> Stereo Pothole adapter --> aligned RGB + shape + mask records
        |                                  |--> RGB-only features ---------+
        |                                  +--> RGB + shape features ------+--> paired metrics
        |
        +--> analytic surfaces --> baseline/current 2D profiles
                                           --> registration --> differencing --> change metrics

All branches --> run manifest + quality flags + plots --> illustrative pre-hardware report
```

Every generated page and figure should carry this caption:

> Pre-hardware software demonstration using public and/or synthetic data. Not a field validation of PaveWatch or the SICK picoScan150.

### Proposed survey-folder layout

Do not commit downloaded datasets. Commit adapters, small synthetic fixtures, manifests, and instructions. Keep local data under an ignored root:

```text
demo-data/
  sources/
    uav-pdd2023/
      LICENSE.txt
      source.json
      archive.sha256
      raw/
    stereo-pothole/
      LICENSE.txt
      source.json
      git-commit.txt
      raw/
  synthetic/
    fixture-v1/
      config.yaml
      truth.parquet
      baseline/
      current/
  normalized/
    samples.parquet
    annotations.parquet
    splits.parquet
  runs/
    <run-id>/
      manifest.json
      metrics.json
      predictions.parquet
      quality_flags.json
      figures/
      report.html
```

### Source manifest example

```json
{
  "source_id": "uav-pdd2023-v4",
  "status": "public-data",
  "title": "UAV-PDD2023",
  "source_url": "https://doi.org/10.5281/zenodo.8429208",
  "retrieved_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "license": "CC-BY-4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "archive_file": "UAV-PDD2023.zip",
  "archive_checksum": "md5:0745d017ce2dce23bd73944e9b0acec7",
  "redistribution": "source files excluded from repository",
  "citation": "Yan and Zhang, 2023, DOI 10.5281/zenodo.8429208"
}
```

### Normalized sample and annotation schemas

`samples.parquet` should contain one row per image, frame, or scan profile:

| Field | Meaning |
|---|---|
| `sample_id` | Stable local identifier, never a raw filename alone. |
| `source_id` | Versioned source manifest identifier. |
| `group_id` | Original flight/sequence/source-photo/near-duplicate cluster used for leakage-safe splitting. |
| `timestamp_ns` | Integer nanoseconds when available; null for independent public images. |
| `modality` | `rgb`, `depth`, `pointcloud`, `profile2d`, `pose`, or `mask`. |
| `relative_uri` | Path relative to the data root. |
| `frame_id` | Coordinate-frame name; null only when the source provides none. |
| `width`, `height` | Raster dimensions where applicable. |
| `units` | Explicit physical units or `pixel`/`unknown`. |
| `calibration_id` | Calibration record or null with a quality flag. |
| `split` | `train`, `validation`, or `test`, assigned by group. |
| `content_hash` | Cryptographic content hash after extraction. |
| `quality_flags` | Missing depth, invalid values, uncertain calibration, synthetic, etc. |

`annotations.parquet` should contain:

| Field | Meaning |
|---|---|
| `annotation_id`, `sample_id` | Provenance keys. |
| `task` | `classification`, `bbox`, `mask`, or `surface_change`. |
| `class_name` | Source class and a separately stored PaveWatch mapping. |
| `geometry` | Box, mask URI, or polygon/profile interval. |
| `value`, `unit` | Known change magnitude for synthetic fixtures; null for visual labels. |
| `source_label` | Original label without silently changing its meaning. |
| `label_quality` | `maintainer`, `synthetic-truth`, `team-reviewed`, or `unknown`. |

### Result record example

```json
{
  "result_id": "fixture-v1-current-heave-001",
  "run_id": "2026-xx-xx_demo_<config-hash>",
  "baseline_sample_ids": ["fixture-v1-baseline-0001"],
  "current_sample_ids": ["fixture-v1-current-0001"],
  "result_type": "candidate_geometric_change",
  "class_name": "heave",
  "location_local_m": [8.0, 1.2],
  "estimated_change_m": null,
  "truth_change_m": 0.03,
  "confidence": null,
  "quality_flags": ["synthetic", "pre-hardware"],
  "requires_field_verification": true
}
```

Nulls in the example are populated only after an algorithm actually produces them. Public visual labels must not be assigned fabricated metric depth or geolocation.

### Interfaces to other investigations

- **02 — picoScan150 acquisition:** must define the real packet/replay format, usable scan angles, scan timing, status fields, invalid-return representation, and proposed altitude/speed cases. The generic simulator configuration should later match those verified facts.
- **03 — RGB/position/time:** must define camera timestamps, intrinsics, distortion, sensor extrinsics, coordinate frames, pose interpolation, and an achievable image ground sampling distance.
- **04 — onboard logging:** must own mission IDs, checksums, folder atomicity, storage format, and raw survey manifests. The normalized adapter should preserve those identifiers.
- **05 — mission planning:** must provide route, speed, altitude, heading, and repeat-survey metadata needed to create profile sequences.
- **06 — processing:** must own the final registration, fusion algorithm, uncertainty model, and performance thresholds. This investigation supplies fixtures, adapters, split policy, and evaluation protocol.
- **08 — reporting:** must own the persistent survey/anomaly schema and report presentation. It should ingest the proposed metrics and quality flags without dropping source provenance.

## 5. Development sequence and dependencies

### Phase 1 — provenance before data

1. Create one machine-readable source manifest per dataset.
2. Save the license text, citation, DOI/version or Git commit, download URL, published checksum, and retrieval date.
3. Add downloaded roots, archives, and generated reports containing source images to `.gitignore`.
4. Verify the archive checksum before extraction and compute SHA-256 hashes after extraction.
5. Require a `--data-root` argument. Scripts must not hide downloads, credentials, or network calls.

### Phase 2 — adapters and dataset audit

1. Parse UAV-PDD2023 VOC XML into the canonical sample/annotation tables.
2. Confirm the repository counts: 2,440 images and 11,158 boxes. Report missing files, invalid boxes, class frequencies, image dimensions, empty images, and duplicate filenames.
3. Cluster exact and near-duplicate images with cryptographic hashes plus a documented perceptual-hash threshold. Keep a cluster in only one split.
4. Preserve the official split as a reference, but create a leakage-audited split if augmented siblings cross official boundaries. Never tune on the held-out test group.
5. Parse all 67 Stereo Pothole frames, verify matching filenames and raster sizes, inspect point-cloud validity, and record the maintainer's listed Dataset 2 evaluation exclusions.

### Phase 3 — synthetic geometric-change experiment

1. Generate one baseline surface and a current surface containing isolated, parameterized deformation fixtures plus an unchanged control region.
2. Sample both surfaces along identical profiles in a noise-free case.
3. Add scenario sweeps one factor at a time: range noise, pose shift, dropout, outliers, scan-spacing reduction, and combined degradation.
4. Fit a local reference surface or profile, register baseline/current data using stable control areas, and calculate residual change.
5. Detect contiguous residuals over a configured magnitude/persistence threshold.
6. Compare estimated location, sign, peak/median magnitude, footprint, and stable-area residual to exact synthetic truth.
7. Export a profile plot, plan-view change map, metrics, quality flags, and an illustrative report.

Parameter sweeps should include a clearly unrealistic stress case so failure is visible. Numerical success thresholds should be selected jointly with investigation 06 and should be tied to injected noise and fixture amplitude, not presented as hardware capability.

### Phase 4 — smallest useful fusion experiment

Use the Stereo Pothole data so both branches see exactly the same frame, label, and split.

1. Partition by the three dataset folders or by verified acquisition sequence, never by randomly mixed patches. A leave-one-group-out evaluation is preferable given the small sample count.
2. Divide each road image into fixed non-overlapping patches or superpixels. Label a patch positive from the provided pothole mask using a declared occupancy rule.
3. **Image-only branch:** calculate simple RGB/texture features such as channel statistics, gradient magnitude, edge density, and local contrast.
4. **Depth-assisted branch:** use the identical RGB features plus point-cloud or disparity-derived shape features such as robust local-plane residual, lower-tail height residual, surface variation, slope, and valid-depth fraction.
5. Train the same class-weighted logistic regression or shallow tree in both branches. Select any threshold using training data only.
6. Evaluate both branches on identical held-out groups. Bootstrap differences by whole frame or sequence, not by patch, so thousands of correlated patches do not create false certainty.
7. Report both results even if depth hurts performance. Do not say “LiDAR improvement”; call it a public stereo-depth fusion result.

This experiment deliberately avoids a large neural network. Its purpose is to prove aligned feature ingestion, controlled ablation, and honest metrics. A later enhancement may train an aerial detector on UAV-PDD2023 and evaluate country/viewpoint transfer using RDD2022.

### Phase 5 — aerial relevance check and report

1. Draw ground-truth UAV-PDD2023 boxes on a deterministic, class-balanced sample without publishing the source images outside allowed attribution conditions.
2. Generate class counts, box-size distributions, image-resolution audit, and examples of quality flags.
3. If laptop resources allow, train a small image-only detector using a framework whose code/model license is acceptable to the team. Keep this optional; document training time and do not compare its score directly with the stereo fusion experiment.
4. Emit one report linking each result to the source manifest, configuration, split, code revision, and raw sample IDs.

## 6. Verification tests and success measures

These checks verify the software demonstration. They are not field-performance acceptance criteria.

### Data and provenance checks

- Every external sample resolves to a source manifest with URL, version, license, access date, citation, and checksum.
- UAV-PDD2023 adapter counts match 2,440 images and 11,158 annotations or produce a blocking discrepancy report.
- Stereo adapter finds 22, 40, and 5 RGB frames and a matching label, disparity, and point-cloud item for every frame.
- Coordinates are in bounds; boxes have positive area; masks use expected values; NaN/Inf depth and missing values are counted.
- No content hash or near-duplicate group crosses train, validation, and test.
- Split generation is deterministic from a stored seed and group table.

### Synthetic-fixture checks

- Re-running the same configuration produces identical source tables and truth values.
- A zero-change current survey produces no injected anomaly and exposes any algorithmic false positives.
- Noise-free, perfectly aligned profiles recover the analytic sample values to numerical tolerance.
- Positive and negative fixtures preserve the correct sign after registration.
- Removing a profile or inserting invalid returns produces a quality flag rather than silent interpolation.
- Changing only one error source changes only the expected configuration and results.

Report at minimum:

- elevation/profile MAE and RMSE against synthetic truth;
- peak and median change error per fixture;
- anomaly localization error and overlap/IoU;
- precision, recall, F1, and false-positive area/rate;
- stable-control residual distribution;
- coverage/completeness; and
- runtime and peak memory.

### Fusion checks

- RGB-only and RGB-plus-shape branches use identical samples, folds, labels, model family, tuning budget, and decision procedure.
- Preprocessing parameters are fitted on training groups only.
- Metrics are calculated per held-out frame/sequence and then aggregated; patches are not treated as independent trials.
- Report PR-AUC, precision, recall, F1, IoU, false-positive rate/area on stable pavement, valid-depth coverage, runtime, and frame-level confidence intervals.
- Publish the paired difference and its uncertainty. Use “improved” only if the actual held-out result and uncertainty support it.
- A shuffled-depth negative control should remove any real advantage. If it does not, inspect leakage or confounding.

### Demonstration completion criteria

The pre-hardware demonstration is complete when a clean laptop can reproduce, from documented inputs:

1. the dataset audit and leakage-safe split tables;
2. a synthetic baseline/current change map with truth-based metrics;
3. paired RGB-only and RGB-plus-shape fusion metrics;
4. a report carrying the mandatory pre-hardware label; and
5. manifests that trace every output to source data, configuration, code revision, and license.

No minimum accuracy percentage should be promised before the experiment is run.

## 7. Cost, mass, power, or resource implications

The demonstration requires no UAV, picoScan150, paid cloud service, or new hardware. It adds no flight mass or power demand.

Planning resources for a normal laptop are:

| Resource | Planning value |
|---|---:|
| UAV-PDD2023 archive | 2.1 GB download plus extracted working copy |
| Stereo Pothole repository | approximately 3.2 GiB |
| RDD2022 full archive, if used | 12.36 GB; avoid by using a country subset |
| RDD2022 China Drone fallback | approximately 153 MB |
| RDD2022 United States fallback | approximately 424 MB |
| SDNET2018 fallback | approximately 504 MB |
| Recommended free disk for core demo | 15–25 GB, including derived data and temporary files |
| Memory | 8 GB workable; 16 GB preferred for high-resolution images and tables |
| Compute | Multicore CPU; GPU optional only for an enhanced neural detector |
| Software/data cost | $0 under the cited terms; network and local storage are existing resources |

Process images and point clouds incrementally rather than loading complete datasets into memory. Cache normalized features with configuration and source hashes. Keep large public data and generated visual reports outside Git; commit only code, small synthetic fixtures, schemas, and aggregate metrics permitted by the source licenses.

## 8. Risks, open decisions, and fallback

### Risks and mitigations

| Risk | Mitigation |
|---|---|
| Public imagery does not match the proposed camera, altitude, pavement, or climate. | Label results as domain-limited; include viewpoint/domain metadata; later build a Mississippi controlled-site dataset. |
| No candidate supplies matched aerial RGB, picoScan150 profiles, pose, and repeat surveys. | Keep public-image, public-fusion, and synthetic-change claims separate; join them only after actual synchronized acquisition. |
| Bounding boxes cannot measure crack width or precise affected area. | Use them only for detection/localization; require team masks or field measurements for dimensions. |
| UAV-PDD2023 augmentation or adjacent frames leak across splits. | Cluster exact and perceptual duplicates and split by provenance group before fitting. |
| The Stereo Pothole set is tiny and correlated. | Split by dataset/sequence, bootstrap whole frames, use simple models, and present uncertainty. |
| Stereo depth is mistaken for picoScan150 evidence. | Name the source and modality on every plot; do not use “LiDAR improvement” for this experiment. |
| Synthetic surfaces make the algorithm look unrealistically clean. | Include pose/noise/dropout stress cases and an unchanged control; publish the generator configuration and failures. |
| Dataset terms change or conflict. | Save license/version metadata at retrieval; prefer DOI archives; do not redistribute raw files; have the university review terms before external publication or commercial reuse. |
| RDD2022 Figshare and maintainer pages state different CC variants. | Treat it as CC BY-SA for derivatives until terms for the exact archive are resolved. |
| A public host or dataset disappears. | Preserve checksums and citations; use the fallback hierarchy below; never rely on an unversioned mirror as the sole source. |
| Large training workloads distract from acquisition and calibration. | Keep the core baseline CPU-scale; make deep detection an enhancement. |

### Fallback hierarchy

1. If UAV-PDD2023 is unavailable, use the RDD2022 China Drone subset for aerial detection and the United States subset for geographic transfer, subject to resolving the license discrepancy.
2. If both UAV sources are unavailable, use SDNET2018 pavement tiles for a clearly labeled binary loader/classifier demonstration.
3. If the Stereo Pothole repository is unavailable, run the fusion interface on synthetic co-registered texture and height maps. Report it as an end-to-end software test with no empirical fusion conclusion.
4. If all public data are unavailable, the analytic baseline/current profile experiment remains fully reproducible and legally unencumbered because the team generates it.
5. After hardware arrives, replace public modalities one adapter at a time while retaining the same canonical schema, quality checks, metrics, and report path.

### Transition to PaveWatch data

| Stage | Data | What becomes testable |
|---|---|---|
| 0 — current | Public RGB/geometry plus analytic profiles | Adapters, leakage controls, deterministic differencing, paired fusion method, provenance, reporting. |
| 1 — bench | Stationary picoScan150 scans of a wall, step, ramp, dark/light targets, plus camera frames | Real packet replay, invalid returns, range repeatability, basic RGB/range alignment, sensor status handling. |
| 2 — controlled ground fixture | Sensor rig over measured pavement boards or known height fixtures | Scan-plane calibration, known-change recovery, surface reflectivity, repeat setup error. |
| 3 — supervised controlled flight | Repeated marked route over an unoccupied permitted site | Motion compensation, timestamp alignment, coverage, pose/registration error, vibration, repeat-flight uncertainty. |
| 4 — local field dataset | Baseline/current Mississippi sidewalk or parking area with independent measurements | Domain performance, false positives, anomaly localization, geometric error, image-only versus picoScan150-assisted comparison. |

Do not fine-tune on the final controlled-site test area before reporting its held-out result. Record source route/segment and survey date as grouping keys so overlapping frames and repeated views cannot cross evaluation boundaries.

### Central decisions still open

1. What geometric changes and physical sizes define the first MVP? Investigation 06 must set this with sensing evidence from investigation 02.
2. What real raw/replay format is canonical: SICK packets, ROS messages/bags, normalized Parquet, or a combination?
3. Which coordinate-frame names, time base, and calibration-file format will investigations 02–04 share?
4. What camera altitude, lens, resolution, and ground sampling distance will make public-image transfer meaningful?
5. Will the application demo include trained aerial detection, or only a dataset audit plus the paired classical fusion baseline?
6. Who reviews dataset licenses before an attachment, repository, model, or derived image is distributed externally?
7. Which report fields and quality flags are mandatory for investigation 08?

## 9. Sources

All sources were accessed **2026-09-19**.

1. Yan, H., and Zhang, J., **UAV-PDD2023 Zenodo record**, dataset description, archive size/checksum, authors, and CC BY 4.0 metadata: https://doi.org/10.5281/zenodo.8429208
2. Yan, H., and Zhang, J., “UAV-PDD2023: A benchmark dataset for pavement distress detection based on UAV images,” *Data in Brief*; image resolution, capture method, weather/road domains, augmentation, and annotation details: https://doi.org/10.1016/j.dib.2023.109692
3. Fan, R., **Stereo Pothole Datasets**, maintainer repository with modalities, frame layout, evaluation note, and MIT license: https://github.com/ruirangerfan/stereo_pothole_datasets
4. Arya, D., et al., **RDD2022 Figshare record**, dataset counts, archive/checksum, scope, and CC BY 4.0 record metadata: https://doi.org/10.6084/m9.figshare.21431547
5. Sekimoto Laboratory, **RoadDamageDetector**, official challenge repository with country-specific downloads, classes, and CC BY-SA 4.0 image statement: https://github.com/sekilab/RoadDamageDetector
6. Arya, D., et al., “RDD2022: A multi-national image dataset for automatic road damage detection,” *Geoscience Data Journal*; capture modalities, resolutions, domains, and annotation details: https://doi.org/10.1002/gdj3.260
7. Maguire, M., Dorafshan, S., and Thomas, R. J., **SDNET2018**, Utah State University dataset record, methodology, archive size, and CC BY 4.0 license: https://doi.org/10.15142/T3TD19
8. Zhao, T., et al., **RSRD project page**, acquisition, modalities, sample counts, splits, and reported precision: https://thu-rsxd.com/rsrd/
9. RSXD maintainers, **RSXD home page**, CC BY-NC and academic-only use statement: https://thu-rsxd.com/
10. Zhao, T., et al., “A road surface reconstruction dataset for autonomous driving,” *Scientific Data*, dataset records and technical validation: https://doi.org/10.1038/s41597-024-03261-9
11. U.S. Geological Survey, **3D Elevation Program**, public availability and program scope: https://www.usgs.gov/3d-elevation-program
12. U.S. Geological Survey, “What is Lidar data and where can I download it?”, general point-cloud description, access paths, and approximately 10 cm vertical-accuracy context: https://www.usgs.gov/faqs/what-lidar-data-and-where-can-i-download-it
13. FuturePave, **PaveSeg-Dataset**, preview/full access statements, image/label description, and repository license: https://github.com/FuturePave/PaveSeg-Dataset
14. Zhu, J., et al., **UAPD Pavement Distress Dataset**, dataset description and “public use” statement without a recognized license: https://github.com/tantantetetao/UAPD-Pavement-Distress-Dataset
15. Karlsruhe Institute of Technology and Toyota Technological Institute at Chicago, **KITTI Vision Benchmark Suite**, modalities and CC BY-NC-SA 3.0 terms: https://www.cvlibs.net/datasets/kitti/
16. Creative Commons, **CC BY 4.0 legal code**: https://creativecommons.org/licenses/by/4.0/legalcode
17. Creative Commons, **CC BY-SA 4.0 legal code**: https://creativecommons.org/licenses/by-sa/4.0/legalcode
18. Creative Commons, **CC BY-NC-SA 3.0 legal code**: https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
