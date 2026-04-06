import streamlit as st
import os
import sqlite3
from datetime import datetime

# 1. 데이터베이스 설정
conn = sqlite3.connect('ebooks.db', check_same_thread=False)
c = conn.cursor()

# 테이블 생성 (기존 테이블이 있다면 그대로 유지됩니다)
c.execute('''CREATE TABLE IF NOT EXISTS books 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              title TEXT, uploader TEXT, category TEXT, 
              file_path TEXT, upload_date TEXT)''')
conn.commit()

# 2. 폴더 설정
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 웹 페이지 레이아웃 및 테마 설정
st.set_page_config(page_title="모두의 도서관 | ShareBook", layout="wide")

# 메인 타이틀 및 소개
st.title("📖 모두의 도서관 (ShareBook)")
st.markdown("---")

# 사이드바: 파일 업로드 섹션
st.sidebar.header("✨ 새로운 책 공유하기")
st.sidebar.write("나만 알고 있기 아까운 지식을 공유해주세요.")

new_title = st.sidebar.text_input("도서 제목", placeholder="예: 파이썬 입문 가이드")
new_uploader = st.sidebar.text_input("닉네임", placeholder="이름 또는 별명")
new_category = st.sidebar.selectbox("카테고리 선택", ["전공/학습", "소설/문학", "자기계발", "IT/기술", "기타"])
uploaded_file = st.sidebar.file_uploader("PDF 파일 업로드", type="pdf")

if st.sidebar.button("공유하기"):
    if uploaded_file and new_title and new_uploader:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        
        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # DB에 정보 기록
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT INTO books (title, uploader, category, file_path, upload_date) VALUES (?, ?, ?, ?, ?)",
                  (new_title, new_uploader, new_category, file_path, now))
        conn.commit()
        st.sidebar.success(f"'{new_title}' 공유가 완료되었습니다!")
        st.balloons()
        st.rerun() # 화면 갱신
    else:
        st.sidebar.error("모든 항목을 입력하고 파일을 선택해주세요.")

# 3. 메인 화면: 공유 목록
st.subheader("📚 최근 공유된 도서 목록")

# 검색 기능 추가 (범용 서비스의 핵심!)
search_query = st.text_input("🔍 찾으시는 도서 제목을 검색해보세요", "")

# DB에서 데이터 읽어오기
if search_query:
    c.execute("SELECT * FROM books WHERE title LIKE ? ORDER BY id DESC", ('%' + search_query + '%',))
else:
    c.execute("SELECT * FROM books ORDER BY id DESC")
    
book_list = c.fetchall()

if book_list:
    # 그리드 스타일로 목록 출력
    for book in book_list:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**[{book[3]}]** {book[1]}") # [카테고리] 제목
                st.caption(f"공유자: {book[2]} | 등록일: {book[5]}")
            with col2:
                # 다운로드 버튼
                with open(book[4], "rb") as f:
                    st.download_button("내려받기", f, file_name=os.path.basename(book[4]), key=f"dl_{book[0]}")
            with col3:
                # 간단한 추천 아이콘 (장식용)
                st.write("⭐ 추천")
            st.write("---")
else:
    if search_query:
        st.warning(f"'{search_query}'에 대한 검색 결과가 없습니다.")
    else:
        st.info("아직 공유된 도서가 없습니다. 왼쪽 메뉴를 통해 첫 번째 지식을 공유해보세요!")