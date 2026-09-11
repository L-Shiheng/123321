import streamlit as st
import random
from datetime import datetime

st.set_page_config(page_title="北京四年级数学同步测试卷", page_icon="📐")

# ========== 题目生成函数 ==========

def gen_dashu(n):
    """大数的认识：读写、比较、改写"""
    questions = []
    for _ in range(n):
        t = random.choice(["read", "compare", "rewrite"])
        if t == "read":
            num = random.randint(10000, 99999999)
            questions.append({
                "q": f"读出下面的数：{num:,}",
                "a": f"{num:,}（读作：{num_to_chinese(num)}）"
            })
        elif t == "compare":
            a = random.randint(100000, 9999999)
            b = random.randint(100000, 9999999)
            symbol = ">" if a > b else "<" if a < b else "="
            questions.append({
                "q": f"比较大小：{a:,} ○ {b:,}",
                "a": f"{a:,} {symbol} {b:,}"
            })
        else:
            num = random.randint(10000, 999999) * 10
            questions.append({
                "q": f"把 {num:,} 改写成用“万”作单位的数",
                "a": f"{num // 10000}万"
            })
    return questions


def gen_yunsuan(n):
    """运算定律：加法/乘法交换律、结合律、分配律"""
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
            a, b = random.randint(5, 25), random.randint(2, 8)
            c = 100 // b if 100 % b == 0 else random.choice([2, 4, 5, 8])
            questions.append({
                "q": f"用简便方法计算：{b} × {a} × {c}",
                "a": f"{a * b * c}（先算 {b} × {c} = {b*c}）"
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
    """角的度量与线与角"""
    questions = []
    for _ in range(n):
        t = random.choice(["du", "ji", "lei"])
        if t == "du":
            deg = random.randint(15, 165)
            questions.append({
                "q": f"一个角是 {deg}°，它是（  ）角。",
                "a": "锐角" if deg < 90 else ("直角" if deg == 90 else "钝角")
            })
        elif t == "ji":
            a = random.randint(30, 120)
            b = random.randint(30, 180 - a)
            questions.append({
                "q": f"∠1 = {a}°，∠2 = {b}°，∠1 + ∠2 = ?",
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
                "q": f"计算：{dividend} ÷ {divisor}",
                "a": f"{quotient}"
            })
        else:
            questions.append({
                "q": f"计算：{dividend} ÷ {divisor}（有余数）",
                "a": f"{quotient} 余 {remainder}"
            })
    return questions


def gen_haoliang(n):
    """认识常见的数量关系"""
    questions = []
    for _ in range(n):
        price = random.randint(5, 50)
        count = random.randint(3, 20)
        questions.append({
            "q": f"每支笔 {price} 元，买 {count} 支一共要多少元？",
            "a": f"{price * count} 元"
        })
    return questions


def num_to_chinese(num):
    """简单数字转中文读法（辅助用）"""
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
    return result if result else "零"


# ========== 页面布局 ==========

st.title("📐 北京四年级数学同步测试卷")
st.caption("按北京版教材知识点自动生成，适合四年级学生练习使用")

# 知识点选项
TOPICS = {
    "1. 大数的认识（读写/比较/改写）": gen_dashu,
    "2. 运算定律（简便计算）": gen_yunsuan,
    "3. 角的度量与线与角": gen_jiaodu,
    "4. 多位数除以两位数": gen_chufa,
    "5. 认识常见的数量关系": gen_haoliang,
}

selected = st.multiselect(
    "选择要测试的知识点（可多选）：",
    list(TOPICS.keys()),
    default=list(TOPICS.keys())[:2]
)

num_per_topic = st.slider("每个知识点出几道题：", 1, 10, 5)

show_answer = st.checkbox("同时显示答案（不勾选则只出题）", value=False)

if st.button("🖨️ 生成测试卷", type="primary"):
    if not selected:
        st.warning("请至少选择一个知识点。")
    else:
        all_questions = []
        for topic in selected:
            qs = TOPICS[topic](num_per_topic)
            all_questions.append((topic, qs))

        st.divider()
        st.header(f"四年级数学测试卷")
        st.caption(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

        idx = 1
        for topic, qs in all_questions:
            st.subheader(f"📌 {topic}")
            for item in qs:
                st.markdown(f"**{idx}.** {item['q']}")
                if show_answer:
                    st.caption(f"答案：{item['a']}")
                idx += 1

        st.divider()
        st.success("试卷生成完成！可以截图或复制题目。")
