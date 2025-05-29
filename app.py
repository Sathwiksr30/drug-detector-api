from fastapi import FastAPI, File, UploadFile, Form
from ultralytics import YOLO
import spacy
from PIL import Image
import io
import keywords
import clip
import torch
import easyocr
import subprocess
import sys

app = FastAPI()
try:
    nlp = spacy.load("en_core_web_sm")
except:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
yolo_model = YOLO("models/yolov8n.pt")
device = "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)
reader = easyocr.Reader(['en'])

@app.post("/content")
async def analyze_content(text: str = Form(...), image: UploadFile = File(...)):
    # Text analysis
    doc = nlp(text.lower())
    text_detections = []
    for token in doc:
        if token.text in keywords.drug_keywords:
            text_detections.append({"keyword": token.text, "category": keywords.drug_keywords.get(token.text, "unknown")})
        if token.text in keywords.coded_slang:
            text_detections.append({"keyword": token.text, "category": keywords.coded_slang[token.text]["category"]})
        if token.text in keywords.drug_hashtags:
            text_detections.append({"keyword": token.text, "category": keywords.drug_hashtags[token.text]["category"]})
        if token.text in keywords.ambiguous_keywords:
            for entry in keywords.ambiguous_keywords[token.text]:
                if entry["category"] != "soda" and entry["category"] != "garden":
                    text_detections.append({"keyword": token.text, "category": entry["category"]})

    # Check suspicious and transaction phrases
    for phrase in keywords.suspicious_phrases:
        if phrase in text.lower():
            text_detections.append({"keyword": phrase, "category": "suspicious"})
    for phrase in keywords.transaction_phrases:
        if phrase in text.lower():
            text_detections.append({"keyword": phrase, "category": "transaction"})

    # Image analysis
    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    yolo_results = yolo_model(img)
    image_detections = []
    for result in yolo_results:
        for box in result.boxes:
            class_name = result.names[int(box.cls)]
            confidence = float(box.conf)
            image_detections.append({"class": class_name, "confidence": confidence})

    # CLIP analysis
    clip_img = preprocess(img).unsqueeze(0).to(device)
    clip_text = clip.tokenize(["pills", "drugs"]).to(device)
    with torch.no_grad():
        image_features = clip_model.encode_image(clip_img)
        text_features = clip_model.encode_text(clip_text)
        logits_per_image, _ = clip_model(clip_img, clip_text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    image_detections.append({"prompt": "pills", "probability": float(probs[0][0])})

    # OCR
    ocr_results = reader.readtext(image_data)
    for (bbox, ocr_text, prob) in ocr_results:
        ocr_text_lower = ocr_text.lower()
        if any(keyword in ocr_text_lower for keyword in keywords.drug_keywords):
            text_detections.append({"keyword": ocr_text_lower, "category": "ocr_drug"})
        if any(keyword in ocr_text_lower for keyword in keywords.coded_slang):
            text_detections.append({"keyword": ocr_text_lower, "category": "ocr_slang"})

    score = sum(d["confidence"] for d in image_detections if "confidence" in d) + len(text_detections)
    return {"results": {"text_detections": text_detections, "image_detections": image_detections, "score": score}, "status": "success"}