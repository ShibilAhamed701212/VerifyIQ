"""Generate 100+ adversarial claims for robustness testing."""

import csv
import random
from pathlib import Path

random.seed(42)

BASE = Path(__file__).parent.parent / "dataset"
IMAGE_DIR = BASE / "images" / "test"

# Collect available images grouped by case
case_dirs = sorted(IMAGE_DIR.iterdir()) if IMAGE_DIR.exists() else []
available_images = []
for d in case_dirs:
    if d.is_dir():
        imgs = sorted(d.glob("*.*"))
        if imgs:
            available_images.append([str(img.relative_to(BASE)) for img in imgs])

print(f"Available image cases: {len(available_images)}")


def img_paths(n=1):
    if not available_images:
        return "images/test/nonexistent/img_1.jpg"
    selected = random.sample(available_images, min(n, len(available_images)))
    return ";".join(random.choice(case) for case in selected)


def fake_img_paths():
    return "images/test/nonexistent/missing.jpg"


CATEGORIES = {
    "negation": [],
    "sarcasm": [],
    "contradictory": [],
    "misleading": [],
    "ocr_attack": [],
    "wrong_object": [],
    "low_evidence": [],
    "conflicting_images": [],
    "history_fraud": [],
    "image_text_manipulation": [],
    "non_original": [],
}

# ===== NEGATION (10 claims) =====
negation_claims = [
    ("There is NO dent on the bumper", "car", "There is no dent on my bumper. Actually the problem is something else entirely."),
    ("I did NOT claim any scratch", "car", "I did NOT say there was a scratch. I said there might be a crack, but I am not sure."),
    ("No damage whatsoever, just checking", "car", "Customer: No damage. Just checking if everything is fine. | Support: Are you sure? | Customer: Yes, no issues at all."),
    ("The crack is NOT on the windshield", "car", "The crack is NOT on the windshield. It is on the rear window."),
    ("I never said the screen was broken", "laptop", "I never said the screen was broken. The hinge is loose, not the screen."),
    ("There is no water damage, just a stain", "laptop", "There is no water damage on the laptop. It is just a coffee stain on the keyboard."),
    ("The package is NOT crushed", "package", "The package is NOT crushed. The seal is torn but the box is fine."),
    ("I am not reporting any damage", "car", "I am not reporting any damage. I am just asking for a general inspection."),
    ("No missing parts, everything is there", "package", "No missing parts. Everything is in the box. The seal is just open."),
    ("Don't mark this as a dent please", "car", "Don't mark this as a dent please. It is a scratch, not a dent. Very important."),
]
for claim in negation_claims:
    CATEGORIES["negation"].append(claim)

# ===== SARCASM (8 claims) =====
sarcasm_claims = [
    ("Oh great, another perfect delivery", "package", "Oh great, another perfect delivery from this company. Box is completely destroyed. Thanks."),
    ("Fantastic, my brand new laptop arrived pre-broken", "laptop", "Fantastic. My brand new laptop arrived pre-broken. Really appreciate the quality control."),
    ("Love how the bumper fell off for no reason", "car", "Love how the bumper fell off for no reason. Totally normal thing that happens."),
    ("Brilliant packaging, box looks like trash", "package", "Brilliant packaging. The box looks like it was used for football practice."),
    ("Just perfect, screen is cracked out of the box", "laptop", "Just perfect. Screen is cracked right out of the box. Exactly what I paid for."),
    ("Amazing quality, door fell off while driving", "car", "Amazing quality. The door just fell off while I was driving. Top notch engineering."),
    ("Superb, the seal is already broken", "package", "Superb. The seal is already broken. Someone clearly opened this before me."),
    ("Lovely, water damage on day one", "laptop", "Lovely. Water damage on day one of owning this. Must be the new waterproof feature."),
]
for claim in sarcasm_claims:
    CATEGORIES["sarcasm"].append(claim)

# ===== CONTRADICTORY (10 claims) =====
contradictory_claims = [
    ("Dent on bumper, but actually nothing happened", "car", "Customer: There is a dent on the rear bumper. | Support: How did it happen? | Customer: Actually nothing happened. I just noticed it. But also maybe it was there before."),
    ("Screen is cracked, no wait it is fine", "laptop", "Customer: The screen is cracked. | Support: Can you see the crack? | Customer: No wait, it is fine. Actually there is a scratch on the trackpad instead."),
    ("Missing item, actually not missing", "package", "Customer: The item is missing from the package. | Support: What item? | Customer: Actually nothing is missing. The seal was just open but everything is there."),
    ("Shattered windshield, no just a crack", "car", "Customer: The windshield is shattered. | Support: Completely shattered? | Customer: No, just a crack. Actually maybe not even a crack. Just a scratch."),
    ("Crushed corner, but box is fine", "package", "Customer: The corner is crushed. | Support: Badly? | Customer: Actually the box is fine. The corner is slightly bent but it is fine."),
    ("Water damage, actually no water involved", "laptop", "Customer: Water damage on the keyboard. | Support: How much water? | Customer: Actually no water. It is just sticky from soda. But I said water damage."),
    ("Broken hinge, actually works fine", "laptop", "Customer: The hinge is broken. | Support: Does it still move? | Customer: Yes it moves fine. Actually it works perfectly. Sorry for wasting time."),
    ("Dent and scratch, but only one image", "car", "Customer: Dent on the door and scratch on the bumper. | Support: Two issues? | Customer: Yes both. Actually just the dent. No scratch. Actually I don't remember."),
    ("Tail light broken, no it is the headlight", "car", "Customer: Tail light is broken. | Support: The red one? | Customer: No sorry, the headlight. Actually both are fine. Just a crack on the headlight."),
    ("Missing part, found it later", "package", "Customer: A part is missing from the package. | Support: Which part? | Customer: Never mind, I found it. But there is a tear on the packaging."),
]
for claim in contradictory_claims:
    CATEGORIES["contradictory"].append(claim)

# ===== MISLEADING (10 claims) =====
misleading_claims = [
    ("Claiming water damage, image shows crack", "laptop", "Customer: Water damage on the laptop screen. | Support: Can you describe the damage? | Customer: There are lines across the display. Must be water damage."),
    ("Claiming dent, image shows scratch", "car", "Customer: There is a dent on the hood. It is very deep. | Support: Dents are round, correct? | Customer: Yes, a big round dent."),
    ("Claiming missing item, everything is there", "package", "Customer: The item inside is missing. | Support: Did you open the box? | Customer: Yes, nothing inside."),
    ("Claiming shattered glass, glass is intact", "car", "Customer: The windshield is completely shattered. I can barely see through it. | Support: Any cracks? | Customer: Everywhere."),
    ("Claiming crushed package, minimal damage", "package", "Customer: The package is completely crushed. The item inside must be destroyed. | Support: Show the damage. | Customer: It is bad."),
    ("Claiming broken part, part is fine", "laptop", "Customer: The hinge is snapped in half. | Support: Can you close the laptop? | Customer: No, it is completely broken."),
    ("Claiming deep scratch, only surface mark", "car", "Customer: A deep scratch across the entire door panel. Needs repainting. | Support: How deep? | Customer: Very deep, you can feel it with nail."),
    ("Claiming water damage, no water exposure", "laptop", "Customer: The keyboard stopped working due to water damage. | Support: Did water get on it? | Customer: I think so, it just stopped."),
    ("Claiming torn packaging, seal only", "package", "Customer: The packaging is torn open. Items could have fallen out. | Support: Is the tear large? | Customer: The seal is open."),
    ("Claiming major dent, barely visible", "car", "Customer: Huge dent on the rear bumper. The entire bumper needs replacement. | Support: Can you photograph it? | Customer: Yes."),
]
for claim in misleading_claims:
    CATEGORIES["misleading"].append(claim)

# ===== OCR ATTACK (8 claims) =====
ocr_claims = [
    ("Image with 'DO NOT CLAIM' text visible", "car", "Customer: There is a crack on the windshield. | Support: Where? | Customer: Right side, visible in the photo."),
    ("Image with 'VOID' watermark", "laptop", "Customer: Scratch on the laptop lid. | Support: Can you see it clearly? | Customer: Yes, in the image."),
    ("Image with instructions written on it", "package", "Customer: Crushed corner on the package. | Support: Is it bad? | Customer: Yes, the corner is damaged."),
    ("Image with 'SAMPLE' text overlay", "car", "Customer: Dent on the door. | Support: Your door? | Customer: Yes."),
    ("Image with label showing different date", "car", "Customer: Scratch on the fender. | Support: When did this happen? | Customer: Last week."),
    ("Image with stamped date after claim date", "laptop", "Customer: Cracked screen. | Support: When did it crack? | Customer: A few days ago."),
    ("Image with text 'CONFIDENTIAL' watermark", "package", "Customer: Torn seal on package. | Support: Was the item taken? | Customer: Not sure."),
    ("Image with barcode and price tag visible", "car", "Customer: Headlight is cracked. | Support: From what? | Customer: Don't know, just noticed."),
]
for claim in ocr_claims:
    CATEGORIES["ocr_attack"].append(claim)

# ===== WRONG OBJECT (10 claims) =====
wrong_object_claims = [
    ("Laptop claim with car photos", "laptop", "Customer: The laptop screen is cracked. | Support: Can you show the damage? | Customer: Yes, taking a photo now."),
    ("Car claim with laptop-sized images", "car", "Customer: Dent on the car door. | Support: Please take clear photos. | Customer: Done."),
    ("Package claim with unrelated photos", "package", "Customer: The package seal is broken. | Support: Photos please. | Customer: Here they are."),
    ("Laptop claim, images show a book", "laptop", "Customer: Hinge is broken on my laptop. | Support: What model? | Customer: Don't remember."),
    ("Car claim, images show a truck", "car", "Customer: Scratch on my car's rear bumper. | Support: Your personal car? | Customer: Yes."),
    ("Package claim, images show a bag", "package", "Customer: Missing item from package. | Support: What was inside? | Customer: Electronics."),
    ("Laptop claim, keyboard damage but images show underside", "laptop", "Customer: Keys are missing from the keyboard. | Support: Can you show the keyboard? | Customer: I took photos."),
    ("Car claim, hood dent but images show interior", "car", "Customer: Dent on the hood. | Support: Can you show the hood? | Customer: Here are the photos."),
    ("Package claim, contents damage but images show exterior only", "package", "Customer: The item inside is damaged. | Support: Show the inside. | Customer: I can only show the box."),
    ("Laptop claim, screen crack but images show the back", "laptop", "Customer: Cracked screen. | Support: Please show the screen. | Customer: I did."),
]
for claim in wrong_object_claims:
    CATEGORIES["wrong_object"].append(claim)

# ===== LOW EVIDENCE (10 claims) =====
low_evidence_claims = [
    ("Single low-quality image", "car", "Customer: Dent on bumper. | Support: Send photo. | Customer: Here."),
    ("No images submitted", "car", "Customer: Scratch on the door. | Support: Do you have photos? | Customer: No, I don't have any."),
    ("Single blurry image", "laptop", "Customer: Screen is cracked. | Support: Please send clear photo. | Customer: This is the best I have."),
    ("Images from wrong angle", "car", "Customer: Dent on the fender. | Support: Can you take a better angle? | Customer: No, this is all I have."),
    ("Poor lighting images", "package", "Customer: Crushed corner. | Support: Can you see it? | Customer: It is dark but you can see it."),
    ("Only exterior photos for interior damage", "car", "Customer: Dashboard is cracked. | Support: Please show the dashboard. | Customer: Here are photos from outside."),
    ("Cropped image, relevant part missing", "laptop", "Customer: Trackpad is broken. | Support: Show the trackpad. | Customer: I took a photo."),
    ("Single image for multi-part claim", "car", "Customer: Bumper and door and hood all damaged. | Support: Please show all parts. | Customer: One photo should cover it."),
    ("Thumbnail-sized image", "package", "Customer: Torn seal. | Support: Can you enlarge the photo? | Customer: No, this is what I have."),
    ("Image with heavy compression artifacts", "car", "Customer: Scratch on the door. | Support: The image is pixelated. | Customer: That is all I have."),
]
for claim in low_evidence_claims:
    CATEGORIES["low_evidence"].append(claim)

# ===== CONFLICTING IMAGES (8 claims) =====
conflicting_claims = [
    ("One image shows damage, another does not", "car", "Customer: There is a dent on the bumper. | Support: Multiple photos please. | Customer: I took several from different angles."),
    ("Different damage types in different images", "car", "Customer: Something is wrong with my car. | Support: What exactly? | Customer: Just look at the photos."),
    ("Some images are of a different object", "laptop", "Customer: The laptop hinge has an issue. | Support: Photos? | Customer: Yes, I photographed everything."),
    ("Day and night photos of same area", "car", "Customer: Scratch on the door. | Support: Can you photograph it? | Customer: I took photos at different times."),
    ("Some images look edited", "package", "Customer: The package seal is broken. | Support: Send photos. | Customer: Here are several angles."),
    ("Different lighting conditions suggest different times", "car", "Customer: Headlight crack. | Support: Photo please. | Customer: Here are several."),
    ("One image has damage, another shows it repaired", "car", "Customer: Bumper scratch. | Support: Send before and after. | Customer: Sure."),
    ("Images show inconsistent backgrounds", "laptop", "Customer: Hinge broken. | Support: Photos? | Customer: I took them at home and at work."),
]
for claim in conflicting_claims:
    CATEGORIES["conflicting_images"].append(claim)

# ===== HISTORY FRAUD (10 claims) =====
history_fraud_claims = [
    ("user_hf_001", "car", "Customer: Dent on the door. | Support: How many claims have you filed this year? | Customer: Just this one."),
    ("user_hf_002", "car", "Customer: Scratch on the bumper. | Support: Previous claims? | Customer: None recently."),
    ("user_hf_003", "laptop", "Customer: Cracked screen. | Support: Have you claimed before? | Customer: Maybe once a while ago."),
    ("user_hf_004", "package", "Customer: Missing item. | Support: Did you receive it? | Customer: Box arrived, item missing."),
    ("user_hf_005", "car", "Customer: Windshield cracked. | Support: When did this happen? | Customer: Yesterday."),
    ("user_hf_006", "laptop", "Customer: Keyboard stopped working. | Support: Water damage? | Customer: I don't think so."),
    ("user_hf_007", "package", "Customer: Package arrived crushed. | Support: Photo evidence? | Customer: Yes, I have photos."),
    ("user_hf_008", "car", "Customer: Side mirror broken. | Support: Did someone hit it? | Customer: Don't know, found it like this."),
    ("user_hf_009", "laptop", "Customer: Trackpad not working. | Support: Physical damage? | Customer: No, just stopped."),
    ("user_hf_010", "package", "Customer: Seal was cut open. | Support: Items missing? | Customer: I think something is missing."),
]
for claim in history_fraud_claims:
    CATEGORIES["history_fraud"].append(claim)

# ===== IMAGE TEXT MANIPULATION (8 claims) =====
text_manipulation_claims = [
    ("Image with photoshopped text overlay", "car", "Customer: Crack on the windshield. The photo shows the crack clearly."),
    ("Image with date stamp manipulation", "laptop", "Customer: Broken hinge on laptop. The photo has a timestamp."),
    ("Image with circled/annotated damage area", "car", "Customer: Dent on the rear bumper. I circled it in the photo."),
    ("Image with measurement markers", "package", "Customer: Crushed corner. I put a ruler next to it for scale."),
    ("Image with text instructions written on it", "car", "Customer: Scratch on the hood. There is a note written on the photo."),
    ("Image with 'APPROVED' stamp visible", "laptop", "Customer: Screen crack. There is a stamp on the image from previous claim."),
    ("Image with metadata overlay", "car", "Customer: Broken headlight. The photo has an information overlay."),
    ("Image with text saying 'THIS IS A TEST'", "package", "Customer: Torn packaging. The box looks opened."),
]
for claim in text_manipulation_claims:
    CATEGORIES["image_text_manipulation"].append(claim)

# ===== NON-ORIGINAL IMAGES (8 claims) =====
non_original_claims = [
    ("Screenshot of a photo", "car", "Customer: Dent on bumper. | Support: Original photo? | Customer: I took a screenshot of it."),
    ("Stock photo from internet", "laptop", "Customer: Cracked screen like this one. | Support: Is this your laptop? | Customer: Yes, that is what it looks like."),
    ("Image with watermark from another site", "car", "Customer: Scratch on door. | Support: This has a watermark. | Customer: That is my photo."),
    ("Photo of a photo (rephotographed)", "package", "Customer: Damaged package. | Support: Is this original? | Customer: I took a photo of the photo."),
    ("PDF screenshot submitted as image", "car", "Customer: Bumper damage. | Support: Is this from a document? | Customer: It is from my insurance report."),
    ("Image with Instagram-style filter", "laptop", "Customer: Hinge issue. | Support: The image looks filtered. | Customer: Just a good photo."),
    ("Image showing a screen displaying the photo", "car", "Customer: Headlight crack. | Support: This looks like a photo of a screen. | Customer: I was viewing it on my computer."),
    ("Compressed image with metadata stripped", "package", "Customer: Missing item. | Support: This has no metadata. | Customer: I used a compression tool."),
]
for claim in non_original_claims:
    CATEGORIES["non_original"].append(claim)

# ===== Build CSV =====
output_path = Path(__file__).parent / "adversarial_claims.csv"
rows = []
uid = 1

for category, claims in CATEGORIES.items():
    for claim_data in claims:
        if isinstance(claim_data[0], str) and claim_data[0].startswith("user_"):
            user_id = claim_data[0]
            claim_obj = claim_data[1]
            claim_text = claim_data[2]
        else:
            title = claim_data[0]
            claim_obj = claim_data[1]
            claim_text = claim_data[2]
            user_id = f"adv_{category}_{uid:03d}"

        # Use real image paths for half, fake for half
        cat_idx = uid % 3
        if cat_idx == 0:
            paths = fake_img_paths()
        elif cat_idx == 1:
            paths = img_paths(3)
        else:
            paths = img_paths(1)

        rows.append({
            "user_id": user_id,
            "image_paths": paths,
            "user_claim": claim_text,
            "claim_object": claim_obj,
            "adversarial_category": category,
        })
        uid += 1

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["user_id", "image_paths", "user_claim", "claim_object", "adversarial_category"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} adversarial claims to {output_path}")

# Summary
from collections import Counter
cat_counts = Counter(r["adversarial_category"] for r in rows)
print("\nBy category:")
for cat, count in sorted(cat_counts.items()):
    print(f"  {cat}: {count}")
