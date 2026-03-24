import streamlit as st
import time

# ─── 初期化 ───────────────────────────────────────────────
def init_state():
    st.session_state.log = []
    st.session_state.current_player = 1
    st.session_state.game_active = False
    st.session_state.game_over = False
    st.session_state.loser = None
    st.session_state.lose_reason = None
    st.session_state.last_word = None
    st.session_state.turn_start = None
    st.session_state.submitted_processed = False

if "log" not in st.session_state:
    init_state()

# ─── ページタイトル ────────────────────────────────────────
st.title("🎮 しりとり Logger")
st.caption("しりとり対決を記録してサポート 😎")

# ─── サイドバー：設定 ──────────────────────────────────────
st.sidebar.header("⚙️ ゲーム設定")
player_count = st.sidebar.number_input("プレイヤー人数", min_value=2, max_value=6, value=2, step=1)
time_limit = st.sidebar.selectbox("制限時間（秒）", [5, 10, 15, 20], index=1)

# ─── スタートボタン ────────────────────────────────────────
if st.button("🟢 スタート / リセット"):
    init_state()
    st.session_state.game_active = True
    st.session_state.turn_start = time.time()
    st.rerun()

# ─── ゲームオーバー表示 ────────────────────────────────────
if st.session_state.game_over:
    st.error(f"💀 プレイヤー {st.session_state.loser} の負け！")
    st.warning(f"理由：{st.session_state.lose_reason}")
    st.info("再スタートするには「スタート / リセット」ボタンを押してください。")

# ─── ゲーム中のUI ──────────────────────────────────────────
if st.session_state.game_active and not st.session_state.game_over:

    st.markdown(f"### 👤 プレイヤー {st.session_state.current_player} の番")

    if st.session_state.last_word:
        st.info(f"前の単語：**{st.session_state.last_word}**　→　「**{st.session_state.last_word[-1]}**」から始めてね！")
    else:
        st.info("最初のプレイヤー！好きな言葉からどうぞ。")

    # ─── 残り時間の計算 ───────────────────────────────────
    elapsed = time.time() - st.session_state.turn_start
    remaining = time_limit - elapsed

    if remaining <= 0:
        st.session_state.game_over = True
        st.session_state.game_active = False
        st.session_state.loser = st.session_state.current_player
        st.session_state.lose_reason = f"制限時間（{time_limit}秒）以内に回答できなかった"
        st.session_state.turn_start = None
        st.rerun()
    else:
        mm, ss = divmod(int(remaining), 60)
        st.metric("⏱ 残り時間", f"{mm:02d}:{ss:02d}")

    # ─── 回答フォーム ──────────────────────────────────────
    with st.form("answer_form", clear_on_submit=True):
        word = st.text_input("回答を入力してください")
        submitted = st.form_submit_button("✅ 回答")

    # ─── 送信処理（二重処理ガード） ────────────────────────
    if submitted and word.strip() and not st.session_state.submitted_processed:
        st.session_state.submitted_processed = True  # 二重実行防止
        word = word.strip()
        lose_reason = None

        if word[-1] == "ん":
            lose_reason = f"「{word}」は「ん」で終わっている"

        elif word in [entry["word"] for entry in st.session_state.log]:
            lose_reason = f"「{word}」はすでに使われた単語"

        elif st.session_state.last_word is not None:
            prev_last_char = st.session_state.last_word[-1]
            normalize = str.maketrans("ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ",
                                      "あいうえおつやゆよわアイウエオツヤユヨワ")
            prev_last_char_n = prev_last_char.translate(normalize)
            word_first_char_n = word[0].translate(normalize)
            if word_first_char_n != prev_last_char_n:
                lose_reason = f"「{st.session_state.last_word[-1]}」ではなく「{word[0]}」から始まっている"

        if lose_reason:
            st.session_state.game_over = True
            st.session_state.game_active = False
            st.session_state.loser = st.session_state.current_player
            st.session_state.lose_reason = lose_reason
            st.session_state.turn_start = None
        else:
            st.session_state.log.append({
                "player": st.session_state.current_player,
                "word": word
            })
            st.session_state.last_word = word
            st.session_state.current_player = (st.session_state.current_player % player_count) + 1
            st.session_state.turn_start = time.time()

        st.rerun()

    # ─── 自動リフレッシュ（タイマー更新用） ────────────────
    # submitted_processedフラグをリセットしつつ、常にsleep+rerunでタイマーを継続
    if st.session_state.submitted_processed:
        st.session_state.submitted_processed = False

    time.sleep(0.5)
    st.rerun()

# ─── 回答ログ表示 ──────────────────────────────────────────
if st.session_state.log:
    st.divider()
    st.subheader("📋 回答ログ")
    for i, entry in enumerate(st.session_state.log, 1):
        st.write(f"{i}. プレイヤー {entry['player']}：**{entry['word']}**")