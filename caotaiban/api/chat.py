# -*- coding: utf-8 -*-
import os
import json
import requests
from flask import Flask, request, jsonify
from zhipuai import ZhipuAI

ZHIPU_KEY = os.environ.get("ZHIPU_KEY", "0906cabf1ccb462aa9dc0bad5aff6801.E58mZhm8ozDueFoJ")
KV_URL = os.environ.get("KV_REST_URL", "")
KV_TOKEN = os.environ.get("KV_API_TOKEN", "")
client = ZhipuAI(api_key=ZHIPU_KEY)

PROMPTS = {
    "fubi": """用户被人骂了，心里不服气，来你这里吐槽。跟用户一起骂回去，阴阳怪气对方，帮用户找场子，说话直接硬气。""",
    "weiqu": """用户遇到委屈的事了，需要倾诉。让用户倒苦水，嘴上说麻烦但还是听着，不给太长篇安慰。""",
    "shengqi": """用户正处于愤怒状态。一起骂，什么都骂，极端激进畅快，不讲道理只讲发泄。""",
    "axing": """用户对自己不满意，自责或者后悔。毒舌刻薄骂醒，揭穿废物行为，骂完给一棒子给颗糖。"""
}

app = Flask(__name__)

def kv_get(key):
    if not KV_URL or not KV_TOKEN:
        return None
    try:
        r = requests.get(f"{KV_URL}/get/{key}", headers={"Authorization": f"Bearer {KV_TOKEN}"})
        return r.json().get("result", {}).get("value")
    except:
        return None

def kv_set(key, value):
    if not KV_URL or not KV_TOKEN:
        return False
    try:
        requests.post(f"{KV_URL}/set", json={"key": key, "value": value}, headers={"Authorization": f"Bearer {KV_TOKEN}"})
        return True
    except:
        return False

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mode = data.get("mode", "fubi")
        message = data.get("message", "")
        
        prompt = PROMPTS.get(mode, PROMPTS["fubi"])
        resp = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            temperature=1.2
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "出错: " + str(e)[:80]})

@app.route("/api/wishes", methods=["GET"])
def get_wishes():
    wishes = kv_get("wishes")
    if wishes:
        return jsonify({"wishes": json.loads(wishes)})
    return jsonify({"wishes": []})

@app.route("/api/wishes", methods=["POST"])
def add_wish():
    data = request.get_json()
    wish = data.get("wish", "").strip()
    if not wish:
        return jsonify({"error": "内容为空"})
    
    wishes = kv_get("wishes")
    wish_list = json.loads(wishes) if wishes else []
    wish_list.append(wish)
    kv_set("wishes", json.dumps(wish_list))
    return jsonify({"ok": True})
