"""数理统计B - 期末复习系统"""
from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, date

app = Flask(__name__)

# 加载数据
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/knowledge")
def knowledge():
    return render_template("knowledge.html")

@app.route("/problems")
def problems():
    return render_template("problems.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/qa")
def qa():
    return render_template("qa.html")

# API路由
@app.route("/api/structure")
def api_structure():
    """返回课程结构数据"""
    return jsonify(load_json("textbook_structure.json"))

@app.route("/api/formulas")
def api_formulas():
    """返回公式数据"""
    return jsonify(load_json("formulas.json"))

@app.route("/api/core_problems")
def api_core_problems():
    """返回人工整理的核心题目"""
    return jsonify(load_json("core_problems.json"))

@app.route("/api/problems")
def api_problems():
    """返回题库，支持筛选"""
    data = load_json("problems.json")
    chapter = request.args.get("chapter", type=int)
    difficulty = request.args.get("difficulty")
    tag = request.args.get("tag")
    source = request.args.get("source")

    problems = data["problems"]
    if chapter:
        problems = [p for p in problems if p["chapter"] == chapter]
    if difficulty:
        problems = [p for p in problems if p["difficulty"] == difficulty]
    if tag:
        problems = [p for p in problems if tag in p.get("tags", [])]
    if source:
        problems = [p for p in problems if p["source"] == source]

    return jsonify({"total": len(problems), "problems": problems})

@app.route("/api/dashboard")
def api_dashboard():
    """返回仪表盘数据"""
    structure = load_json("textbook_structure.json")
    problems = load_json("problems.json")

    # 考试倒计时
    exam_date = date(2026, 7, 1)
    days_left = (exam_date - date.today()).days

    # 各章题目数
    ch_problem_count = {}
    for p in problems["problems"]:
        ch = p["chapter"]
        ch_problem_count[ch] = ch_problem_count.get(ch, 0) + 1

    # 难度分布
    diff_count = {"easy": 0, "medium": 0, "hard": 0}
    for p in problems["problems"]:
        d = p.get("difficulty", "medium")
        diff_count[d] = diff_count.get(d, 0) + 1

    return jsonify({
        "course": structure["course"],
        "days_left": days_left,
        "exam_date": "2026-07-01",
        "total_chapters": len(structure["chapters"]),
        "total_problems": problems["total"],
        "chapters": [{"id": ch["id"], "title": ch["title"], "importance": ch["importance"],
                       "sections_count": len(ch["sections"]),
                       "problem_count": ch_problem_count.get(ch["id"], 0)}
                      for ch in structure["chapters"]],
        "difficulty_distribution": diff_count
    })

@app.route("/api/knowledge")
def api_knowledge():
    """返回指定知识点的详细讲解"""
    chapter = request.args.get("chapter", "")
    section = request.args.get("section", "")
    topic = request.args.get("topic", "")

    content = load_json("knowledge_content.json")

    if chapter and section and topic:
        try:
            return jsonify(content[chapter][section][topic])
        except KeyError:
            return jsonify({"error": "知识点未找到"}), 404
    elif chapter:
        try:
            return jsonify(content[chapter])
        except KeyError:
            return jsonify({"error": "章节未找到"}), 404
    else:
        return jsonify({"chapters": list(content.keys())})

@app.route("/api/faq")
def api_faq():
    """返回FAQ数据"""
    faqs = [
        {"q": "χ²分布、t分布、F分布之间的关系是什么？", "a": "t²(n) = F(1,n)；t(∞) = N(0,1)；χ²(n)/n → 1 (n→∞)；F(m,∞) = χ²(m)/m", "tags": ["分布", "三大分布"]},
        {"q": "矩估计和极大似然估计的区别？", "a": "矩估计用样本矩代替总体矩，计算简单但不一定最优；MLE通过最大化似然函数求参数，通常具有渐近有效性，但有时计算复杂。在大样本下MLE通常更优。", "tags": ["估计", "MLE"]},
        {"q": "置信区间和假设检验的关系？", "a": "两者是等价的：置信水平1-α的置信区间包含θ₀，等价于水平α的检验不拒绝H₀: θ=θ₀。区间估计给出参数的可能范围，假设检验对特定值做判断。", "tags": ["区间估计", "假设检验"]},
        {"q": "什么是p值？如何用p值做检验？", "a": "p值是在H₀为真时，观察到比当前样本更极端结果的概率。决策规则：若p < α，拒绝H₀；若p ≥ α，不拒绝H₀。p值越小，对H₀的证据越强。", "tags": ["p值", "假设检验"]},
        {"q": "第I类错误和第II类错误有什么区别？", "a": "第I类错误（α）：H₀为真时拒绝H₀（弃真）；第II类错误（β）：H₀为假时不拒绝H₀（取伪）。通常控制α，然后最小化β。增大样本量可以同时减小两类错误。", "tags": ["两类错误", "假设检验"]},
        {"q": "什么是充分统计量？", "a": "统计量T(X)称为充分的，如果给定T(X)后，样本的条件分布不依赖于参数θ。直观理解：T(X)包含了样本中关于θ的全部信息。可用因子分解定理判断。", "tags": ["充分统计量", "估计"]},
        {"q": "UMVUE是什么？如何求UMVUE？", "a": "UMVUE（一致最小方差无偏估计）是在所有无偏估计中方差最小的。求法：(1)找到充分完备统计量；(2)找该统计量的函数使其为无偏估计。", "tags": ["UMVUE", "估计"]},
        {"q": "单因素方差分析的基本假设是什么？", "a": "(1)各总体独立且服从正态分布；(2)各总体方差相等（方差齐性）；(3)各观测值相互独立。方差分析对正态性不太敏感，但对方差异常敏感。", "tags": ["方差分析", "ANOVA"]},
        {"q": "贝叶斯估计与经典估计（频率学派）的核心区别？", "a": "贝叶斯将参数视为随机变量，有先验分布π(θ)，利用样本信息更新得到后验分布π(θ|x)，然后基于后验分布做推断。经典估计视参数为未知常数，仅利用样本信息。", "tags": ["贝叶斯", "估计"]},
        {"q": "如何理解Cramér-Rao下界？", "a": "C-R下界给出了无偏估计量方差的下界（1/(nI(θ))）。如果一个无偏估计的方差达到了C-R下界，它就是UMVUE。Fisher信息量I(θ)衡量了样本中包含θ信息的多少。", "tags": ["C-R不等式", "估计"]},
    ]
    return jsonify({"faqs": faqs})

if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_ENV") != "production"
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=debug, port=port, host="0.0.0.0")
