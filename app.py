from fastapi import FastAPI, File, UploadFile, Form
from ultralytics import YOLO
import spacy
from PIL import Image
import io
import keywords
import clip
import torch
import easyocr

app = FastAPI()
nlp = spacy.load("en_core_web_sm")
yolo_model = YOLO("models/yolov8n.pt")
device = "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)
reader = easyocr.Reader(['en'])

@app.post("/content")
async def analyze_content(text: str = Form(...), image: UploadFile = File(...)):
    # Process text with SpaCy
    doc = nlp(text.lower())
    text_detections = []
    seen_keywords = set()
    text_lower = text.lower()

    # Check drug keywords
    for keyword in keywords.drug_keywords:
        if keyword in text_lower and (keyword, "drug") not in seen_keywords:
            text_detections.append({"keyword": keyword, "category": keywords.drug_keywords.get(keyword, "unknown")})
            seen_keywords.add((keyword, "drug"))

    # Check coded slang
    for keyword in keywords.coded_slang:
        if keyword in text_lower and (keyword, "slang") not in seen_keywords:
            text_detections.append({"keyword": keyword, "category": keywords.coded_slang[keyword]["category"]})
            seen_keywords.add((keyword, "slang"))

    # Check drug hashtags
    for keyword in keywords.drug_hashtags:
        if keyword in text_lower and (keyword, "hashtag") not in seen_keywords:
            text_detections.append({"keyword": keyword, "category": keywords.drug_hashtags[keyword]["category"]})
            seen_keywords.add((keyword, "hashtag"))

    # Check ambiguous keywords
    for keyword in keywords.ambiguous_keywords:
        if keyword in text_lower:
            for entry in keywords.ambiguous_keywords[keyword]:
                if entry["category"] not in ["soda", "garden"] and (keyword, entry["category"]) not in seen_keywords:
                    text_detections.append({"keyword": keyword, "category": entry["category"]})
                    seen_keywords.add((keyword, entry["category"]))

    # SpaCy token-based checks
    for token in doc:
        if token.text in keywords.drug_keywords and (token.text, "drug") not in seen_keywords:
            text_detections.append({"keyword": token.text, "category": keywords.drug_keywords.get(token.text, "unknown")})
            seen_keywords.add((token.text, "drug"))
        if token.text in keywords.coded_slang and (token.text, "slang") not in seen_keywords:
            text_detections.append({"keyword": token.text, "category": keywords.coded_slang[token.text]["category"]})
            seen_keywords.add((token.text, "slang"))
        if token.text in keywords.drug_hashtags and (token.text, "hashtag") not in seen_keywords:
            text_detections.append({"keyword": token.text, "category": keywords.drug_hashtags[token.text]["category"]})
            seen_keywords.add((token.text, "hashtag"))
        if token.text in keywords.ambiguous_keywords:
            for entry in keywords.ambiguous_keywords[token.text]:
                if entry["category"] not in ["soda", "garden"] and (token.text, entry["category"]) not in seen_keywords:
                    text_detections.append({"keyword": token.text, "category": entry["category"]})
                    seen_keywords.add((token.text, entry["category"]))

    # Check suspicious and transaction phrases
    for phrase in keywords.suspicious_phrases:
        if phrase in text_lower and (phrase, "suspicious") not in seen_keywords:
            text_detections.append({"keyword": phrase, "category": "suspicious"})
            seen_keywords.add((phrase, "suspicious"))
    for phrase in keywords.transaction_phrases:
        if phrase in text_lower and (phrase, "transaction") not in seen_keywords:
            text_detections.append({"keyword": phrase, "category": "transaction"})
            seen_keywords.add((phrase, "transaction"))

    # Process image
    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data)).convert("RGB")

    # YOLO detection
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

    # OCR with EasyOCR
    ocr_results = reader.readtext(image_data)
    for (bbox, ocr_text, prob) in ocr_results:
        ocr_text_lower = ocr_text.lower()
        if any(keyword in ocr_text_lower for keyword in keywords.drug_keywords) and (ocr_text_lower, "ocr_drug") not in seen_keywords:
            text_detections.append({"keyword": ocr_text_lower, "category": "ocr_drug"})
            seen_keywords.add((ocr_text_lower, "ocr_drug"))
        if any(keyword in ocr_text_lower for keyword in keywords.coded_slang) and (ocr_text_lower, "ocr_slang") not in seen_keywords:
            text_detections.append({"keyword": ocr_text_lower, "category": "ocr_slang"})
            seen_keywords.add((ocr_text_lower, "ocr_slang"))

    # Calculate score
    score = sum(d["confidence"] for d in image_detections if "confidence" in d) + len(text_detections)
    return {"results": {"text_detections": text_detections, "image_detections": image_detections, "score": score}, "status": "success"}