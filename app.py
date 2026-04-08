from datetime import datetime

import streamlit as st

from auth import login_ui, get_user, logout
from engine import generate_today_actions
from storage import (
    add_history_entry,
    get_last_tasks,
    get_recent_history_text,
    get_streak,
    load_data,
    save_tasks,
    update_profile,
    update_streak_if_completed_today,
)

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="Do This Today", page_icon="🔥", layout="centered")

# =========================
# 登入系統
# =========================
user = get_user()

if not user:
    login_ui()
    st.stop()

# 顯示登入資訊
st.success(f"已登入：{user.email}")

col1, col2 = st.columns([4, 1])
with col2:
    if st.button("登出"):
        logout()
        st.rerun()

# =========================
# 主標題
# =========================
st.title("🔥 Do This Today")
st.caption("AI 幫你決定今天最該做的 3 件事")

# =========================
# 載入資料（目前還是本地版）
# =========================
data = load_data()
profile = data["profile"]

# =========================
# 使用者設定
# =========================
with st.expander("1. 設定你的個人資料", expanded=True):
    goal = st.text_input("你的主要目標", value=profile.get("goal", ""))
    weakness = st.text_input("你的主要弱點", value=profile.get("weakness", ""))
    notes = st.text_area("補充背景", value=profile.get("notes", ""), height=120)

    if st.button("儲存個人資料"):
        update_profile(goal, weakness, notes)
        st.success("已儲存")

# =========================
# 任務生成
# =========================
st.divider()
st.subheader("2. 生成今天的 3 件事")

col1, col2 = st.columns(2)
with col1:
    st.metric("目前 streak", f"{get_streak()} 天")
with col2:
    st.metric("最近紀錄", f"{len(data.get('history', []))} 筆")

if st.button("給我今天該做的事", type="primary"):
    try:
        history_text = get_recent_history_text()
        tasks = generate_today_actions(goal, weakness, notes, history_text)
        save_tasks(tasks)
        st.success("今天任務已生成")
    except Exception as e:
        st.error(str(e))

# =========================
# 顯示任務
# =========================
tasks = get_last_tasks()

if tasks:
    st.divider()
    st.subheader("3. 今天的任務")

    completed_actions = []
    skipped_actions = []

    for i, task in enumerate(tasks, start=1):
        st.markdown(f"### {i}. {task['title']}")
        st.write(f"**原因：** {task['reason']}")
        st.write(f"**預估時間：** {task['estimated_minutes']} 分鐘")

        status = st.radio(
            f"任務 {i} 狀態",
            ["未選擇", "已完成", "跳過"],
            key=f"status_{i}",
            horizontal=True,
        )

        if status == "已完成":
            completed_actions.append(task["title"])
        elif status == "跳過":
            skipped_actions.append(task["title"])

    reflection = st.text_area("今天的簡短反思（可不填）", height=100)

    if st.button("儲存今天紀錄"):
        add_history_entry(
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "completed_actions": completed_actions,
                "skipped_actions": skipped_actions,
                "reflection": reflection,
            }
        )

        if completed_actions:
            streak = update_streak_if_completed_today()
            st.success(f"已儲存，streak 目前 {streak} 天")
        else:
            st.warning("已儲存，但今天沒有完成任何任務，所以 streak 不增加")

    # =========================
    # 分享文字
    # =========================
    st.divider()
    st.subheader("4. 分享")

    share_lines = ["🔥 Today AI told me to:"]
    for i, task in enumerate(tasks, start=1):
        share_lines.append(f"{i}. {task['title']}")
    share_lines.append("")
    share_lines.append("Built with Do This Today")

    share_text = "\n".join(share_lines)

    st.code(share_text, language="text")
    st.caption("可以貼到 IG / Threads")

else:
    st.info("先按『給我今天該做的事』來生成任務")

# =========================
# 歷史紀錄
# =========================
st.divider()

with st.expander("5. 最近紀錄"):
    history = data.get("history", [])

    if not history:
        st.write("還沒有紀錄")
    else:
        for item in reversed(history[-7:]):
            st.markdown(f"**{item['date']}**")
            st.write(
                f"完成：{', '.join(item['completed_actions']) if item['completed_actions'] else '無'}"
            )
            st.write(
                f"跳過：{', '.join(item['skipped_actions']) if item['skipped_actions'] else '無'}"
            )
            if item.get("reflection"):
                st.write(f"反思：{item['reflection']}")
            st.markdown("---")