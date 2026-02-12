import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TRANSFORMERS_NO_FLAX"] = "1"

from flask import Flask, request, jsonify, render_template
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# =========================
# CONFIG
# =========================
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
ADAPTER_PATH = "MyFinetunedModel_TinyLlama"
DEVICE = "cpu"   # Safe for Windows without GPU

# =========================
# CREATE APP
# =========================
app = Flask(__name__)

# =========================
# LOAD MODEL
# =========================
print("🔄 Loading TinyLlama tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("🔄 Loading TinyLlama base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float32
).to(DEVICE)

print("🔄 Attaching LoRA adapter...")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

# Fix padding token if missing
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("✅ Environment TinyLlama model loaded successfully")

# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# CHAT API
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("message", "").strip()

    if not question:
        return jsonify({"response": "Please enter a question."})

    prompt = f"Human: {question}\nAssistant:"
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id
        )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = answer.split("Assistant:")[-1].strip()

    return jsonify({"response": answer})

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)
