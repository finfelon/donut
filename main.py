# main.py
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)


# 데이터 로드 및 강건한 전처리 함수
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 1. 텍스트 열 결측치 처리 및 장르 추출 (.str 전용 안전 메서드)
    df["genre"] = df["genre"].fillna("미상").astype(str).str.split("|").str[0]
    df["nation"] = df["nation"].fillna("기타").astype(str)
    df["movieNm"] = df["movieNm"].fillna("제목없음").astype(str)

    # 2. 숫자형 열 수치 변환 (쉼표 제거 및 결측치 0 처리)
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ""), errors="coerce"
            ).fillna(0)

    # 3. 선버스트/트리맵용 개수 컬럼
    df["movie_count"] = 1

    return df


df = load_data()

# 메인 타이틀
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 중 해당 기간 개봉작 216편의 데이터입니다."
)
st.markdown("---")

# ---------------------------------------------------------
# 1. 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------
st.subheader("1. 장르별 영화 편수")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = px.pie(
    genre_counts,
    values="count",
    names="genre",
    hole=0.4,
    title="장르별 영화 편수 비율",
)
fig1.update_traces(
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

st.plotly_chart(fig1, use_container_width=True)
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 영화 중 특정 인기 장르가 차지하는 비중과 전체적인 장르 분포 편차를 확인할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 2. 장르 및 영화별 총 관객수 분포 (트리맵)
# ---------------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객수 분포")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객수 트리맵",
    color="genre",
)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명<extra></extra>",
    texttemplate="<b>%{label}</b><br>%{value:,.0f}명",
)

st.plotly_chart(fig2, use_container_width=True)
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 장르별 총 흥행 규모와 함께 각 장르 내에서 어떤 영화가 관객수를 독점하거나 주도했는지 한눈에 비교할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 3. 총 관객수 분포 (히스토그램)
# ---------------------------------------------------------
st.subheader("3. 영화별 총 관객수 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객수 구간별 영화 수 분포",
    labels={"total_audi": "총 관객수", "count": "영화 수"},
)
fig3.update_traces(
    hovertemplate="관객수 구간: %{x:,.0f}명<br>영화 수: %{y}편<extra></extra>",
    marker_color="#1f77b4",
)
fig3.update_layout(yaxis_title="영화 수 (편)")

st.plotly_chart(fig3, use_container_width=True)

# 주요 통계 데이터 산출
top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = int(top_movie_row["total_audi"])

under_2m_count = int((df["total_audi"] <= 2000000).sum())
under_2m_ratio = (under_2m_count / len(df)) * 100

st.markdown(
    f"""
    - **관객수 집중 구간:** 전체 {len(df)}편 중 **{under_2m_count}편({under_2m_ratio:.1f}%)**의 영화가 **200만 명 이하** 구간에 집중되어 있습니다.
    - **최다 관객 동원 영화:** 최다 관객을 기록한 영화는 **'{top_movie_name}'**(총 관객수 **{top_movie_audi:,}명**)입니다.
    """
)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 대다수 영화의 관객수는 하위 구간에 모여 있는 반면, 극소수의 메가 히트작이 전체 박스오피스 상위 관객수를 크게 견인하는 롱테일 양상을 확인할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 4. 개봉일 스크린수와 총 관객수의 관계 (산점도)
# ---------------------------------------------------------
st.subheader("4. 개봉일 스크린수와 총 관객수의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수 대비 총 관객수 산점도",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "genre": "장르",
    },
)

fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,.0f}개<br>총 관객수: %{y:,.0f}명<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 초기 스크린 확보 수량이 최종 관객수에 미치는 양의 상관관계와, 스크린수가 적음에도 높은 관객수를 기록한 '알짜 흥행작'을 식별할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 5. 주요 장르별 총 관객수 분포 (박스플롯)
# ---------------------------------------------------------
st.subheader("5. 주요 장르별 총 관객수 분포 (10편 이상 장르)")

genre_counts_series = df["genre"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index
df_filtered = df[df["genre"].isin(top_genres)]

fig5 = px.box(
    df_filtered,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="영화 수 10편 이상 장르의 관객수 박스플롯",
    labels={"genre": "장르", "total_audi": "총 관객수 (명)"},
    points="outliers",
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>장르: %{x}<br>총 관객수: %{y:,.0f}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 주요 장르별 흥행의 중간값(중위수)과 편차 범위, 그리고 상자 밖의 독보적인 흥행 대작(이상치 영화)들을 한눈에 비교할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 6. 스크린수, 총 관객수, 첫 주 관객수의 관계 (버블 그래프)
# ---------------------------------------------------------
st.subheader("6. 개봉일 스크린수, 총 관객수, 첫 주 관객수 (버블 그래프)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    custom_data=["first_week_audi"],
    size_max=40,
    title="개봉일 스크린수 대비 총 관객수 및 첫 주 관객수 버블 그래프",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "genre": "장르",
        "first_week_audi": "개봉 첫 주 관객수 (명)",
    },
)

fig6.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,.0f}개<br>총 관객수: %{y:,.0f}명<br>개봉 첫 주 관객: %{customdata[0]:,.0f}명<extra></extra>"
)

st.plotly_chart(fig6, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 점의 크기(첫 주 관객수)를 통해 초반 흥행 몰이가 최종 관객수에 얼마나 큰 영향을 미치는지 입체적으로 파악할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 7. 제작 국가 및 장르별 영화 편수 (선버스트 그래프)
# ---------------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트 그래프)")

fig7 = px.sunburst(
    df,
    path=[px.Constant("전체 국가"), "nation", "genre"],
    values="movie_count",
    title="제작 국가별 주력 장르 선버스트",
    color="nation",
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
)

st.plotly_chart(fig7, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 특정 국가에서 어떤 장르의 영화를 많이 제작하여 개봉했는지, 국가 간 주력 장르의 차이를 계층적으로 파악할 수 있습니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 8. 10위권 유지 일수와 총 관객수 (장르별 몰입도 및 롱런 산점도)
# ---------------------------------------------------------
st.subheader("8. 10위권 유지 일수 대비 총 관객수 (장르별 흥미도/롱런 분석)")

fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="10위권 머문 날수 대비 총 관객수 산점도",
    labels={
        "days_in_top10": "10위권 유지 일수 (일)",
        "total_audi": "총 관객수 (명)",
        "genre": "장르",
    },
)

fig8.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>10위권 유지 일수: %{x}일<br>총 관객수: %{y:,.0f}명<extra></extra>"
)

st.plotly_chart(fig8, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 관객의 높은 몰입도로 이탈 없이 롱런한 영화(오랫동안 10위권을 유지하며 고관객을 달성한 작품)와 특정 장르의 흥행 지속력을 분석할 수 있습니다."
)
