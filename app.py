import streamlit as st

SIZE = 8
EMPTY, BLACK, WHITE = 0, 1, -1
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


def initial_board():
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    board[3][3] = board[4][4] = WHITE
    board[3][4] = board[4][3] = BLACK
    return board


def inside(row, col):
    return 0 <= row < SIZE and 0 <= col < SIZE


def flips_for(board, row, col, player):
    if board[row][col] != EMPTY:
        return []
    flips = []
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        line = []
        while inside(r, c) and board[r][c] == -player:
            line.append((r, c))
            r, c = r + dr, c + dc
        if line and inside(r, c) and board[r][c] == player:
            flips.extend(line)
    return flips


def legal_moves(board, player):
    return {(r, c): flips_for(board, r, c, player)
            for r in range(SIZE) for c in range(SIZE)
            if flips_for(board, r, c, player)}


def place(board, row, col, player, flips):
    next_board = [line[:] for line in board]
    next_board[row][col] = player
    for r, c in flips:
        next_board[r][c] = player
    return next_board


def score(board):
    black = sum(cell == BLACK for row in board for cell in row)
    white = sum(cell == WHITE for row in board for cell in row)
    return black, white


def reset_game():
    st.session_state.board = initial_board()
    st.session_state.player = BLACK
    st.session_state.notice = "黒の番です。置けるマスを選んでください。"


st.set_page_config(page_title="オセロ", page_icon="⚫", layout="centered")
st.title("⚫ オセロ")
st.caption("黒・白の2人対戦。緑の点が置ける場所です。")

if "board" not in st.session_state:
    reset_game()

board = st.session_state.board
player = st.session_state.player
moves = legal_moves(board, player)
other_moves = legal_moves(board, -player)

if not moves and other_moves:
    st.session_state.player = -player
    st.session_state.notice = f"{'黒' if player == BLACK else '白'}は置けないためパス。"
    st.rerun()

black, white = score(board)
st.subheader(f"黒 {black} — {white} 白")
st.info(st.session_state.notice)

symbols = {EMPTY: "", BLACK: "●", WHITE: "○"}
for r in range(SIZE):
    cols = st.columns(SIZE, gap="small")
    for c, col in enumerate(cols):
        label = symbols[board[r][c]] or ("·" if (r, c) in moves else " ")
        disabled = (r, c) not in moves
        if col.button(label, key=f"cell-{r}-{c}", disabled=disabled,
                      use_container_width=True):
            st.session_state.board = place(board, r, c, player, moves[(r, c)])
            next_player = -player
            next_moves = legal_moves(st.session_state.board, next_player)
            own_moves = legal_moves(st.session_state.board, player)
            if not next_moves and not own_moves:
                final_black, final_white = score(st.session_state.board)
                result = "黒の勝ち" if final_black > final_white else "白の勝ち" if final_white > final_black else "引き分け"
                st.session_state.notice = f"ゲーム終了：{result}！"
            elif not next_moves:
                st.session_state.player = player
                st.session_state.notice = f"{'黒' if next_player == BLACK else '白'}はパス。続けてどうぞ。"
            else:
                st.session_state.player = next_player
                st.session_state.notice = f"{'黒' if next_player == BLACK else '白'}の番です。"
            st.rerun()

st.button("新しいゲーム", on_click=reset_game)
