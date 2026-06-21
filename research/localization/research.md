# Visual Localization Research

## Overview

This document evaluates object detection and segmentation models for
integration with VerifyIQ V2. The goal is to add spatial grounding to
damage claims — detecting bounding boxes for claimed object parts and
segmenting damage regions directly in image space.

## Candidate Models

### YOLOv8 / YOLOv11 (Ultralytics)

| Property | Value |
|----------|-------|
| Type | Object detection, instance segmentation |
| Model size | YOLOv8n: 3.2MB, YOLOv8x: 68MB |
| Inference | ~2ms on GPU, ~50ms on CPU (YOLOv8n) |
| VRAM | ~1GB for nano, ~6GB for x-large |
| Training | Fine-tuning requires ~100-500 labeled images |
| Integration | `pip install ultralytics`, single-line inference |

**Pros:** Fastest option, pre-trained on COCO (car parts, screens,
packages). Easy to fine-tune on damage-specific classes.

**Cons:** Requires labeled bounding box data for fine-tuning. COCO classes
don't include damage-specific categories (dent, scratch, crack).

**Recommendation:** Use YOLOv8n for object part detection (car door,
bumper, screen, keyboard, package seal) — fine-tune on 200 labeled images
from the dataset. Do NOT use for damage classification directly.

### Grounding DINO

| Property | Value |
|----------|-------|
| Type | Open-set object detection |
| Model size | ~700MB (Swin-T), ~1.4GB (Swin-B) |
| Inference | ~100ms on GPU |
| VRAM | ~4GB for tiny, ~8GB for base |
| Integration | `pip install groundingdino-py` or detectron2 |

**Pros:** Zero-shot — no training needed. Detects any object described in
text ("car door with dent", "cracked laptop screen"). Can detect damage
categories directly.

**Cons:** Heavy model, slow inference, unreliable for very subtle damage.
Requires GPU for practical inference speed.

**Recommendation:** Use as an optional enhancement when YOLO confidence
< 0.6. Text-prompt "damage on {part}" for open-set damage detection.

### SAM / SAM2 (Meta)

| Property | Value |
|----------|-------|
| Type | Segmentation |
| Model size | SAM: ~2.4GB, SAM2: ~700MB |
| Inference | ~200ms on GPU (with prompt) |
| VRAM | ~5GB (SAM), ~3GB (SAM2 tiny) |
| Integration | `pip install segment-anything` |

**Pros:** Best-in-class segmentation — produces pixel-perfect masks.
Prompt with bounding box from YOLO or text from Grounding DINO.

**Cons:** Very heavy, CPU inference impractical. Does NOT classify — only
segments. Needs a detection model to provide prompts.

**Recommendation:** Run only on GPU, only when YOLO + Grounding DINO
disagree. Use SAM2 (lighter, faster) over original SAM.

## Integration Plan

```
Input Image
    │
    ▼
YOLOv8n (part detection)
    │
    ├── confidence > 0.7 → bounding box, part label
    │
    └── confidence < 0.7
            │
            ▼
        Grounding DINO (open-set detection)
            │
            └── SAM2 (segmentation mask)
                    │
                    ▼
            Damage region mask → evidence trace
```

## Resource Requirements

| Model | VRAM | CPU Inference | GPU Inference | Storage |
|-------|------|---------------|---------------|---------|
| YOLOv8n | ~1GB | ~50ms/image | ~2ms/image | 3MB |
| YOLOv8x | ~6GB | ~300ms/image | ~5ms/image | 68MB |
| Grounding DINO (T) | ~4GB | N/A | ~100ms/image | 700MB |
| SAM2 tiny | ~3GB | N/A | ~100ms/image | 700MB |

## Verdict

**Do NOT deploy heavy models in the competition pipeline.** Add YOLOv8n
(3MB, CPU-friendly) for object part verification. SAM2 and Grounding DINO
are post-competition enhancements.

### V2 Integration

```python
# Stub — YOLO integration for Phase 2
# from ultralytics import YOLO
# model = YOLO("yolov8n.pt")
# results = model("image.jpg")
# detected_parts = [r.names[int(c)] for r in results[0].boxes]
```
