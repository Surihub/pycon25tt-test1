##########################################################
# 1️⃣ 시나리오 1: 공개 Google Sheet - URL 직접 삽입
##########################################################

import streamlit as st
import pandas as pd

st.title("1️⃣ ✅ 공개 Google Sheet 읽기")
st.info("📘 누구나 볼 수 있도록 공개된 시트를 Pandas로 직접 불러오는 가장 간단한 방법입니다.\n📎 링크는 반드시 `export?format=csv` 형태로 설정하세요.")

csv_url1 = "https://docs.google.com/spreadsheets/d/1VC_q8HJfIufjGVR2zGRcJjBgkefIbp6Pv01rQ1uvoXI/export?format=csv"
df1 = pd.read_csv(csv_url1)
st.dataframe(df1)

##########################################################
# 2️⃣ 시나리오 2: 공개 Google Sheet - URL을 secrets.toml에 저장
##########################################################

# import streamlit as st
# import pandas as pd

# st.title("2️⃣ 🔐 공개 Google Sheet 읽기")
# st.info("📘 Sheet는 여전히 공개 상태입니다. URL만 안전하게 숨기기 위해 `secrets.toml`에 저장합니다.")


# csv_url2 = st.secrets["gsheet_public_csv_url"]
# df2 = pd.read_csv(csv_url2)

# # 📄 시트 전체 미리보기
# st.dataframe(df2, use_container_width=True)

# # 🔍 활성화된 질문 필터링
# active_rows = df2[df2["is_active"] == True]

# if active_rows.empty:
#     st.warning("⚠️ 현재 활성화된 질문이 없습니다.")
# else:
#     for i, row in active_rows.iterrows():
#         st.divider()
#         st.subheader(f"📌 질문: {row['question_text']}")
        
#         # 선택지 opt_a, opt_b, opt_c, ... 자동 추출
#         options = [row[col] for col in df2.columns if col.startswith("opt_") and pd.notna(row[col])]
        
#         # 사용자 응답 입력
#         selected = st.radio(
#             f"답을 골라주세요 (질문 ID: {row['question_id']})",
#             options,
#             key=f"question_{i}"
#         )

#         # ✅ 정답 확인
#         correct = row["answer"]
#         if selected:
#             if selected == correct:
#                 st.success("✅ 정답입니다!")
#             else:
#                 st.error(f"❌ 오답입니다. 정답은 **{correct}** 입니다.")

#########################################################
# 3️⃣ 시나리오 3: 비공개 Google Sheet — 읽고 쓰기
##########################################################

# import streamlit as st
# import gspread
# import pandas as pd
# from google.oauth2.service_account import Credentials

# st.title("3️⃣ 🔒 비공개 Google Sheet 연결")
# st.info("🔐 시트에 ‘공개 설정 없이’ 안전하게 접근하려면 서비스 계정을 사용해야 합니다.\n📎 서비스 계정 이메일을 시트에 ‘뷰어’ 또는 ‘편집자’로 공유하세요.")

# SCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]
# credentials = Credentials.from_service_account_info(
#     st.secrets["google_service_account"],
#     scopes=SCOPES
# )
# gc = gspread.authorize(credentials)
# spreadsheet = gc.open_by_key(st.secrets["gsheet_key"])
# sheet_input = spreadsheet.worksheet("datainput")

# def append_input_data(name, feedback):
#     sheet_input.append_row([name, feedback])

# with st.form("input_form"):
#     name = st.text_input("이름")
#     feedback = st.text_area("피드백")
#     submitted = st.form_submit_button("제출")

#     if submitted:
#         if name and feedback:
#             append_input_data(name, feedback)
#             st.success("✅ 저장 완료")
#         else:
#             st.warning("⚠️ 모든 필드를 입력해 주세요.")

# # 화면에 출력
# st.markdown("---")
# st.subheader("📊 지금까지 제출된 데이터")
# df = pd.DataFrame(sheet_input.get_all_records())

# if st.button("새로고침 🔄"):
#     st.cache_data.clear()
# st.write(df['피드백'])

##########################################################
# 5️⃣ 시나리오 4: 🎼 청중 DJ 투표 시스템 (한 사람당 1회만 투표)
##########################################################

import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
import altair as alt

st.set_page_config(page_title="청중 DJ 투표", layout="wide")
st.title("5️⃣ 🎼 청중 DJ — 오늘의 배경음악 투표")
st.info("🙋‍♀️ 한 사람당 한 번만 투표 가능하며, 실시간 투표 결과를 원그래프로 확인할 수 있습니다!")

# 🎵 장르 선택지
OPTIONS = {
    "🎧 Chill": "Chill",
    "🔥 EDM": "EDM",
    "🧘‍♂️ Classic": "Classic",
    "🕺 Funk": "Funk"
}

# 인증
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=SCOPES
)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(st.secrets["gsheet_key"]).worksheet("bgm")

# 사용자 고유 ID
if "client_id" not in st.session_state:
    st.session_state["client_id"] = str(uuid.uuid4())[:8]
client_id = st.session_state["client_id"]

# 기존 투표 불러오기
@st.cache_data(ttl=2)
def load_votes():
    rows = sheet.get_all_records()
    df = pd.DataFrame(rows)
    return df if not df.empty else pd.DataFrame(columns=["timestamp", "genre", "client_id"])

votes_df = load_votes()
already_voted = client_id in votes_df["client_id"].values

# 투표 저장 함수
def append_vote(genre: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([ts, genre, client_id])
    st.cache_data.clear()

# 투표 UI
st.subheader("📥 장르 선택")
if already_voted:
    st.success("✅ 이미 투표하셨습니다. 감사합니다!")
else:
    cols = st.columns(len(OPTIONS))
    for i, (emoji, genre) in enumerate(OPTIONS.items()):
        if cols[i].button(emoji, use_container_width=True):
            append_vote(genre)
            st.success(f"'{genre}'에 투표되었습니다!")
            st.rerun()

st.divider()

# 결과 시각화
st.subheader("📊 실시간 투표 결과")
if votes_df.empty:
    st.info("아직 투표가 없습니다. 첫 번째 DJ가 되어보세요 🎧")
else:
    agg = votes_df["genre"].value_counts().reset_index()
    agg.columns = ["genre", "count"]
    agg["pct"] = (agg["count"] / agg["count"].sum() * 100).round(1)

    chart = alt.Chart(agg).mark_arc(innerRadius=50).encode(
        theta="count:Q",
        color="genre:N",
        tooltip=["genre", "count", "pct"]
    ).properties(height=360)

    st.altair_chart(chart, use_container_width=True)
    st.markdown(f"**총 투표 수:** {agg['count'].sum()}명")

if st.button("🔄 결과 새로고침"):
    st.cache_data.clear()
    st.rerun()
