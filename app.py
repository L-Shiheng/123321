import streamlit as st
import streamlit.components.v1 as components
import random
from datetime import datetime
from io import BytesIO
from openai import OpenAI
import pandas as pd

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
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_html(sections, show_answer=False, title="四年级数学同步测试卷"):
    now = datetime.now().strftime("%Y-%m-%d")

    body = []
    idx = 1
    for topic, qs in sections:
        body.append(f'<h2>{esc(topic)}</h2>')
        for item in qs:
            body.append(
                f'<div class="q"><span class="num">{idx}.</span> {esc(item["q"])}</div>'
            )
            if show_answer and item.get("a"):
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
  <title>{esc(title)}</title>
  {css}
</head>
<body>
  <div class="paper">
    <h1>{esc(title)}</h1>
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


# ==================== 题库读取与模板 ====================

@st.cache_data(show_spinner=False)
def load_bank(file_bytes, file_name):
    if file_name.lower().endswith(".csv"):
        try:
            return pd.read_csv(BytesIO(file_bytes))
        except UnicodeDecodeError:
            return pd.read_csv(BytesIO(file_bytes), encoding="gbk")
    else:
        return pd.read_excel(BytesIO(file_bytes))


def make_template():
    data = {
        "知识点": [
            "大数的认识", "大数的认识", "运算定律", "运算定律",
            "角的度量", "角的度量", "多位数除法", "多位数除法",
            "数量关系", "数量关系"
        ],
        "题型": ["填空", "填空", "计算", "计算", "填空", "计算", "计算", "计算", "解答", "解答"],
        "题干": [
            "读出下面的数：12345678",
            "把 50000 改写成用“万”作单位的数是（　　）万。",
            "用简便方法计算：25 × 36",
            "用简便方法计算：125 × 8 × 5",
            "一个角是 75°，它是（　　）角。",
            "一个角是 40°，它的补角是（　　）度。",
            "计算：936 ÷ 24",
            "计算：1275 ÷ 51",
            "每本笔记本 8 元，买 15 本一共要多少元？",
            "一辆汽车每小时行 65 千米，4 小时能行多少千米？"
        ],
        "答案": [
            "一千二百三十四万五千六百七十八",
            "5",
            "900（25×4×9）",
            "5000（125×8=1000，1000×5=5000）",
            "锐角",
            "140",
            "39",
            "25",
            "120 元",
            "260 千米"
        ],
        "难度": ["简单", "简单", "中等", "中等", "简单", "中等", "中等", "困难", "简单", "中等"]
    }
    df = pd.DataFrame(data)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="题库")
    return buf.getvalue()


# ==================== 页面标题 ====================

st.title("📐 北京四年级数学同步测试卷")
st.caption("支持自动出题和题库抽题，可下载打印，还配有 AI 老师答疑")

tab1, tab2 = st.tabs(["🎲 自动出题", "📚 从题库出题"])


# ==================== Tab1：自动出题 ====================

with tab1:
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
        default=list(TOPICS.keys())[:2],
        key="auto_topics"
    )

    num_per_topic = st.slider("每个知识点出几道题：", 1, 10, 5, key="auto_num")

    if st.button("🖨️ 生成试卷", type="primary", key="auto_btn"):
        if not selected:
            st.warning("请至少选择一个知识点。")
        else:
            sections = []
            for topic in selected:
                sections.append((topic, TOPICS[topic](num_per_topic)))
            st.session_state["sections"] = sections
            st.session_state["paper_title"] = "四年级数学同步测试卷"
            st.rerun()


# ==================== Tab2：题库出题 ====================

with tab2:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.download_button(
            "📄 下载题库模板 (Excel)",
            data=make_template(),
            file_name="题库模板.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="tpl_btn"
        )
    with col2:
        st.caption("模板包含：**知识点、题型、题干、答案、难度** 五列。按此格式整理你的题库，或直接在模板上修改。")

    uploaded = st.file_uploader(
        "上传题库文件（支持 .xlsx / .xls / .csv）",
        type=["xlsx", "xls", "csv"],
        key="bank_upload"
    )

    if uploaded is None:
        st.info("👆 请先上传题库文件。没有现成的题库？点左边的按钮下载模板，填好后再上传。")
    else:
        try:
            df = load_bank(uploaded.getvalue(), uploaded.name)
        except Exception as e:
            st.error(f"❌ 读取文件失败：{e}")
            df = None

        if df is not None:
            required = ["知识点", "题干"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error(f"❌ 题库缺少必要的列：{'、'.join(missing)}。请参考模板调整后重新上传。")
            else:
                df = df.dropna(subset=["题干"]).copy()
                if "答案" not in df.columns:
                    df["答案"] = ""
                if "题型" not in df.columns:
                    df["题型"] = ""
                if "难度" not in df.columns:
                    df["难度"] = ""

                df["知识点"] = df["知识点"].astype(str).str.strip()
                df["难度"] = df["难度"].fillna("").astype(str).str.strip()

                st.success(f"✅ 题库加载成功，共 **{len(df)}** 道题。")

                # 难度筛选
                diff_options = sorted([d for d in df["难度"].unique() if d != "" and d.lower() != "nan"])
                if diff_options:
                    picked_diff = st.multiselect(
                        "按难度筛选（不选则不限难度）：",
                        diff_options,
                        default=[],
                        key="diff_filter"
                    )
                    if picked_diff:
                        df = df[df["难度"].isin(picked_diff)]

                # 分布统计
                st.markdown("**📊 题库分布：**")
                stats = df.groupby("知识点").size().reset_index(name="题目数量")
                st.dataframe(stats, use_container_width=True, hide_index=True)

                # 抽题设置
                st.markdown("**🎯 设置每个知识点抽几道题：**")
                topics = list(df["知识点"].unique())
                plan = {}
                cols = st.columns(2)
                for i, topic in enumerate(topics):
                    cnt = int((df["知识点"] == topic).sum())
                    with cols[i % 2]:
                        plan[topic] = st.number_input(
                            f"{topic}（共 {cnt} 题）",
                            min_value=0,
                            max_value=cnt,
                            value=min(5, cnt),
                            key=f"bank_num_{topic}"
                        )

                if st.button("🎯 从题库抽题生成试卷", type="primary", key="bank_btn"):
                    total = sum(plan.values())
                    if total == 0:
                        st.warning("请至少给一个知识点设置抽题数量。")
                    else:
                        sections = []
                        for topic, cnt in plan.items():
                            if cnt <= 0:
                                continue
                            sub = df[df["知识点"] == topic]
                            rows = sub.sample(n=min(cnt, len(sub))).to_dict("records")
                            qs = []
                            for r in rows:
                                q_text = str(r["题干"]).strip()
                                t_type = str(r.get("题型", "")).strip()
                                if t_type and t_type.lower() != "nan":
                                    q_text = f"（{t_type}）{q_text}"
                                ans = r.get("答案", "")
                                ans = "" if ans is None or str(ans).lower() == "nan" else str(ans)
                                qs.append({"q": q_text, "a": ans})
                            sections.append((topic, qs))
                        st.session_state["sections"] = sections
                        st.session_state["paper_title"] = "四年级数学测试卷（题库版）"
                        st.rerun()


# ==================== 试卷展示 & 下载 ====================

if st.session_state.get("sections"):
    sections = st.session_state["sections"]
    title = st.session_state.get("paper_title", "四年级数学同步测试卷")

    st.divider()
    st.header("📝 试卷预览")

    html_blank = build_html(sections, show_answer=False, title=title)
    html_answer = build_html(sections, show_answer=True, title=title)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.download_button(
            "📥 下载空白卷（打印用）",
            data=html_blank.encode("utf-8"),
            file_name=f"{title}.html",
            mime="text/html",
            use_container_width=True,
            type="primary",
            key="dl_blank"
        )
    with c2:
        st.download_button(
            "📥 下载含答案卷（老师用）",
            data=html_answer.encode("utf-8"),
            file_name=f"{title}_含答案.html",
            mime="text/html",
            use_container_width=True,
            key="dl_ans"
        )
    with c3:
        if st.button("🗑️ 清空当前试卷", use_container_width=True, key="clear_paper"):
            st.session_state.pop("sections", None)
            st.rerun()

    st.info(
        "**打印方法：** 下载后双击打开文件（浏览器会自动打开）→ 按 `Ctrl + P`（Mac：`Cmd + P`）→ "
        "选打印机打印，或选择“另存为 PDF”。打印时建议勾选“背景图形”，否则虚线答题线可能不显示。"
    )

    with st.expander("👀 预览试卷效果（空白卷）", expanded=True):
        components.html(html_blank, height=900, scrolling=True)


# ==================== AI 老师 ====================

st.divider()
st.header("👨‍🏫 AI 老师")
st.caption("做完题有不懂的地方，可以在这里问 AI 老师。")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def get_api_key():
    try:
        return st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        return None


api_key = get_api_key()

if not api_key:
    st.warning(
        "⚠️ 还没有配置 DeepSeek API Key。\n\n"
        "**在 Streamlit Cloud 上部署**：进入你的应用 → 右下角 **⋮** → **Settings** → **Secrets**，填入：\n\n"
        "```\nDEEPSEEK_API_KEY = \"sk-你的密钥\"\n```\n\n"
        "保存后等待几十秒，页面会自动刷新。"
    )
else:
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🗑️ 清空对话", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("向 AI 老师提问，例如：12 × (5 + 6) 怎么用简便方法算？")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            try:
                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

                messages = [{
                    "role": "system",
                    "content": (
                        "你是一位耐心的小学四年级数学老师，面向北京地区四年级学生。"
                        "用简单易懂的语言讲解题目，步骤要清晰，语气要亲切。"
                        "涉及计算时要写出完整过程，适当举例子。"
                    )
                }] + st.session_state.chat_history

                stream = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=2048
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "Authentication" in error_msg:
                    st.error("❌ API Key 无效，请检查 Secrets 中的 DEEPSEEK_API_KEY。")
                elif "429" in error_msg:
                    st.error("❌ 请求太频繁，请稍后再试。")
                elif "Connection" in error_msg or "timeout" in error_msg.lower():
                    st.error("❌ 网络连接失败，请检查网络后重试。")
                else:
                    st.error(f"❌ 出错了：{error_msg}")
