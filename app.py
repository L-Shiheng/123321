import streamlit as st
import streamlit.components.v1 as components
import random
from datetime import datetime

st.set_page_config(page_title="北京四年级数学同步测试卷", page_icon="📐", layout="wide")


# ==================== 数字转中文（辅助） ====================
def num_to_chinese(num):
    digits = "零一二三四五六七八九"
    units = ["", "十", "百", "千", "万", "十万", "百万", "千万"]
    s = str(num)
    result = ""
    zero_flag = False
    length = len(s)
    for i, ch in enumerate(s):
        d = int(ch)
        pos = length - i - 1
        if d == 0:
            zero_flag = True
        else:
            if zero_flag and result:
                result += "零"
            result += digits[d] + units[pos]
            zero_flag = False
    if result.startswith("一十") and length == 2:
        result = result[1:]
    return result if result else "零"


# ==================== 各知识点题目生成函数 ====================

def gen_dashu(n):
    """大数的认识"""
    questions = []
    for _ in range(n):
        t = random.choice(["read", "compare", "rewrite"])
        if t == "read":
            num = random.randint(10000, 99999999)
            questions.append({
                "q": f"读出下面的数：{num:,}",
                "a": f"{num:,} 读作 {num_to_chinese(num)}"
            })
        elif t == "compare":
            a = random.randint(100000, 9999999)
            b = random.randint(100000, 9999999)
            symbol = ">" if a > b else "<" if a < b else "="
            questions.append({
                "q": f"比较大小：{a:,} ○ {b:,}（在○里填上 >、< 或 =）",
                "a": f"{a:,} {symbol} {b:,}"
            })
        else:
            num = random.randint(1, 9999) * 10000
            questions.append({
                "q": f"把 {num:,} 改写成用“万”作单位的数。",
                "a": f"{num // 10000} 万"
            })
    return questions


def gen_yunsuan(n):
    """运算定律"""
    questions = []
    for _ in range(n):
        t = random.choice(["jiafa", "chengfa", "fenpei"])
        if t == "jiafa":
            a, b, c = [random.randint(10, 99) for _ in range(3)]
            questions.append({
                "q": f"用简便方法计算：{a} + {b} + {c}",
                "a": f"{a + b + c}（先算能凑整的两个数）"
            })
        elif t == "chengfa":
            a = random.randint(5, 25)
            b = random.choice([2, 4, 5, 8])
            c = random.choice([5, 25])
            questions.append({
                "q": f"用简便方法计算：{b} × {a} × {c}",
                "a": f"{a * b * c}（先算 {b} × {c} = {b * c}）"
            })
        else:
            a = random.randint(10, 50)
            b, c = random.randint(2, 9), random.randint(2, 9)
            questions.append({
                "q": f"用简便方法计算：{a} × ({b} + {c})",
                "a": f"{a * (b + c)}（{a}×{b} + {a}×{c}）"
            })
    return questions


def gen_jiaodu(n):
    """角的度量"""
    questions = []
    for _ in range(n):
        t = random.choice(["du", "ji", "bu"])
        if t == "du":
            deg = random.randint(15, 165)
            questions.append({
                "q": f"一个角是 {deg}°，它是（ 　 ）角。",
                "a": "锐角" if deg < 90 else ("直角" if deg == 90 else "钝角")
            })
        elif t == "ji":
            a = random.randint(30, 120)
            b = random.randint(30, 180 - a)
            questions.append({
                "q": f"已知 ∠1 = {a}°，∠2 = {b}°，求 ∠1 + ∠2 是多少度？",
                "a": f"{a + b}°"
            })
        else:
            a = random.randint(30, 80)
            questions.append({
                "q": f"一个角是 {a}°，它的补角是多少度？",
                "a": f"{180 - a}°"
            })
    return questions


def gen_chufa(n):
    """多位数除以两位数"""
    questions = []
    for _ in range(n):
        divisor = random.randint(11, 99)
        quotient = random.randint(10, 99)
        remainder = random.randint(0, divisor - 1)
        dividend = divisor * quotient + remainder
        if remainder == 0:
            questions.append({
                "q": f"计算：{dividend} ÷ {divisor} =",
                "a": f"{quotient}"
            })
        else:
            questions.append({
                "q": f"计算：{dividend} ÷ {divisor} =（有余数）",
                "a": f"{quotient} 余 {remainder}"
            })
    return questions


def gen_haoliang(n):
    """常见数量关系"""
    questions = []
    for _ in range(n):
        price = random.randint(5, 50)
        count = random.randint(3, 20)
        questions.append({
            "q": f"每支笔 {price} 元，买 {count} 支一共需要多少元？",
            "a": f"{price * count} 元"
        })
    return questions


# ==================== HTML 试卷生成 ====================

def esc(s):
    """转义 HTML 特殊字符"""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(sections, show_answer=False):
    """把题目列表拼成一整页可打印的 HTML"""
    now = datetime.now().strftime("%Y-%m-%d")

    body = []
    idx = 1
    for topic, qs in sections:
        body.append(f'<h2>{esc(topic)}</h2>')
        for item in qs:
            body.append(
                f'<div class="q"><span class="num">{idx}.</span> {esc(item["q"])}</div>'
            )
            if show_answer:
                body.append(f'<div class="ans">答案：{esc(item["a"])}</div>')
            else:
                body.append('<div class="space"></div>')
            idx += 1

    css = """
    <style>
      @page { size: A4; margin: 15mm 14mm; }
      * { box-sizing: border-box; }
      body {
        font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", "SimSun", sans-serif;
        color: #111; font-size: 15px; line-height: 1.8;
        margin: 0; padding: 20px; background: #f0f0f0;
      }
      .paper {
        max-width: 800px; margin: 0 auto; background: #fff;
        padding: 30px 34px; box-shadow: 0 2px 12px rgba(0,0,0,.1);
      }
      h1 { text-align: center; font-size: 24px; margin: 0 0 16px; letter-spacing: 4px; }
      .meta {
        display: flex; justify-content: space-between; flex-wrap: wrap;
        font-size: 14px; padding-bottom: 10px; margin-bottom: 18px;
        border-bottom: 2px solid #333;
      }
      .meta span { margin-right: 12px; }
      h2 {
        font-size: 16px; margin: 22px 0 10px; padding-left: 10px;
        border-left: 4px solid #2c7be5; page-break-after: avoid;
      }
      .q { margin: 10px 0 6px; page-break-inside: avoid; }
      .q .num { font-weight: bold; margin-right: 6px; }
      .ans { color: #c0392b; font-size: 13px; margin: 0 0 10px 26px; }
      .space { height: 34px; border-bottom: 1px dashed #ccc; margin: 0 26px 10px; }
      .tip { text-align: center; color: #888; font-size: 12px; margin-top: 30px; }
      @media print {
        body { background: #fff; padding: 0; font-size: 14px; }
        .paper { box-shadow: none; padding: 0; max-width: 100%; }
        .space { height: 32px; }
        .tip { display: none; }
      }
    </style>
    """

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>四年级数学同步测试卷</title>
  {css}
</head>
<body>
  <div class="paper">
    <h1>四年级数学同步测试卷</h1>
    <div class="meta">
      <span>姓名：____________</span>
      <span>班级：____________</span>
      <span>日期：{now}</span>
      <span>得分：__________</span>
    </div>
    {''.join(body)}
    <div class="tip">—— 试卷结束 ——</div>
  </div>
</body>
</html>"""


# ==================== 页面 ====================

st.title("📐 北京四年级数学同步测试卷")
st.caption("按北京版教材知识点自动生成，可下载打印")

TOPICS = {
    "一、大数的认识（读写 / 比较 / 改写）": gen_dashu,
    "二、运算定律（简便计算）": gen_yunsuan,
    "三、角的度量与线与角": gen_jiaodu,
    "四、多位数除以两位数": gen_chufa,
    "五、认识常见的数量关系": gen_haoliang,
}

selected = st.multiselect(
    "选择要测试的知识点（可多选）：",
    list(TOPICS.keys()),
    default=list(TOPICS.keys())[:2]
)

col1, col2 = st.columns(2)
with col1:
    num_per_topic = st.slider("每个知识点出几道题：", 1, 10, 5)
with col2:
    blank_lines = st.radio("每题下方预留作答空间：", ["一行", "两行"], horizontal=True)

if st.button("🖨️ 生成试卷", type="primary"):
    if not selected:
        st.warning("请至少选择一个知识点。")
    else:
        # 生成题目
        sections = []
        for topic in selected:
            sections.append((topic, TOPICS[topic](num_per_topic)))

        # 保存到 session_state，避免下载时重新随机
        st.session_state["sections"] = sections

# ==================== 展示 & 下载 ====================

if "sections" in st.session_state:
    sections = st.session_state["sections"]

    html_blank = build_html(sections, show_answer=False)
    html_answer = build_html(sections, show_answer=True)

    st.success("试卷已生成，可以下载打印了 👇")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 下载试卷（空白卷，用于打印）",
            data=html_blank.encode("utf-8"),
            file_name="四年级数学测试卷.html",
            mime="text/html",
            use_container_width=True,
            type="primary",
        )
    with c2:
        st.download_button(
            label="📥 下载试卷（含答案，老师用）",
            data=html_answer.encode("utf-8"),
            file_name="四年级数学测试卷_含答案.html",
            mime="text/html",
            use_container_width=True,
        )

    st.info(
        "**怎么打印？** 下载后双击打开文件（会自动用浏览器打开）→ "
        "按 `Ctrl + P`（Mac 是 `Cmd + P`）→ 选择打印机打印，"
        "或者选择“另存为 PDF”保存成 PDF 文件。"
    )

    with st.expander("👀 预览试卷效果（空白卷）", expanded=True):
        components.html(html_blank, height=900, scrolling=True)
