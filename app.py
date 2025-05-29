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
             # Text analysis
             doc = nlp(text.lower())
             text_detections = []
             for token in doc:
                 if token.text in keywords.drug_keywords:
                     text_detections.append({"keyword": token.text, "category": keywords.drug_categories.get(token.text, "unknown")})

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
                 if any(keyword in ocr_text.lower() for keyword in keywords.drug_keywords):
                     text_detections.append({"keyword": ocr_text.lower(), "category": "ocr_drug"})

             score = sum(d["confidence"] for d in image_detections if "confidence" in d) + len(text_detections)
             return {"results": {"text_detections": text_detections, "image_detections": image_detections, "score": score}, "status": "success"}