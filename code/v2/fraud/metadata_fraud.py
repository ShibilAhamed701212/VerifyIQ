from code.v2.models.fraud import MetadataFraudResult


class MetadataFraudDetector:
    """Detects EXIF anomalies, editing software, timestamp mismatches."""

    def check(self, image_paths: list[str]) -> MetadataFraudResult:
        result = MetadataFraudResult()
        if not image_paths:
            return result

        editing_software_found = set()
        cameras = set()
        timestamps = []

        for p in image_paths:
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                img = Image.open(p)
                exif = img._getexif()
                if exif:
                    result.has_exif = True
                    for tag_id, value in exif.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        if tag_name == "Software":
                            editing_software_found.add(str(value))
                            result.has_editing = True
                        elif tag_name == "Model":
                            cameras.add(str(value))
                        elif tag_name == "DateTimeOriginal":
                            timestamps.append(str(value))
                else:
                    result.flags.append("no_exif")
            except Exception:
                result.flags.append("exif_read_error")

        if editing_software_found:
            result.editing_software = "; ".join(editing_software_found)
        if len(cameras) > 1:
            result.camera_mismatch = list(cameras)
        if len(set(timestamps)) > 1 and len(timestamps) > 1:
            result.timestamp_mismatch = True

        score = 0.0
        if result.has_editing:
            score += 0.3
            result.flags.append("edited_image")
        if result.timestamp_mismatch:
            score += 0.3
            result.flags.append("timestamp_mismatch")
        if result.camera_mismatch:
            score += 0.2
            result.flags.append("camera_mismatch")
        if "no_exif" in result.flags:
            score += 0.1

        result.fraud_score = min(1.0, score)
        return result
