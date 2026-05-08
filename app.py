from __future__ import annotations

import asyncio
import os
from pathlib import Path
import uuid

import streamlit as st

from router import route
from tools.file_tools import (
    WORKING_DIR_ENV_VAR,
    get_current_branch_name,
    get_working_dir,
    is_git_repository,
)


AGENT_MODES = ["自動", "リサーチ", "コード", "ドキュメント"]
SUGGESTIONS = {
    ":blue[:material/rate_review:] 変更差分をレビュー": "今の変更差分をレビューしてください。重大度順で指摘してください。",
    ":green[:material/bug_report:] バグ調査": "最近起きやすいバグの原因候補を挙げて、確認手順を提案してください。",
    ":orange[:material/description:] 仕様整理": "このアプリの主要機能を箇条書きで整理してください。",
}


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_mode" not in st.session_state:
        st.session_state.agent_mode = "自動"
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "working_dir" not in st.session_state:
        st.session_state.working_dir = str(Path.cwd().resolve())
    if "working_dir_input" not in st.session_state:
        st.session_state.working_dir_input = st.session_state.working_dir


def _apply_working_dir(path_text: str) -> tuple[bool, str]:
    candidate = Path(path_text).expanduser()
    if not candidate.is_absolute():
        return False, "作業ディレクトリは絶対パスで入力してください。"
    if not candidate.exists():
        return False, "指定したパスが存在しません。"
    if not candidate.is_dir():
        return False, "指定したパスはディレクトリではありません。"

    resolved = str(candidate.resolve())
    st.session_state.working_dir = resolved
    os.environ[WORKING_DIR_ENV_VAR] = resolved
    return True, "作業ディレクトリを更新しました。"


async def stream_text(prompt: str, mode: str, session_id: str, placeholder) -> str:
    agent = route(prompt, mode, session_id)
    chunks: list[str] = []
    async for event in agent.stream_async(prompt):
        if "data" in event:
            chunks.append(event["data"])
            placeholder.markdown("".join(chunks))
    return "".join(chunks)


def main() -> None:
    st.set_page_config(page_title="Personal Agent Platform", page_icon="🤖")
    st.title("Personal Agent Platform")
    st.caption("エージェントと対話しながら開発作業を進められます")
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] .block-container {
            padding-bottom: 7rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_state()
    os.environ[WORKING_DIR_ENV_VAR] = st.session_state.working_dir

    with st.sidebar:
        st.subheader("作業ディレクトリ")
        st.text_input(
            "絶対パス",
            key="working_dir_input",
            placeholder="/path/to/project",
        )
        if st.button("作業ディレクトリを適用", use_container_width=True):
            ok, message = _apply_working_dir(st.session_state.working_dir_input)
            if ok:
                st.success(message)
            else:
                st.error(message)

        working_dir = get_working_dir()
        st.caption(f"作業ディレクトリ: `{working_dir.name or str(working_dir)}`")
        if is_git_repository():
            branch_name = get_current_branch_name() or "-"
            st.caption(f"ブランチ: `{branch_name}`")
        else:
            st.caption("ブランチ: `-`")

        st.divider()
        st.session_state.agent_mode = st.radio(
            "エージェント選択",
            AGENT_MODES,
            index=AGENT_MODES.index(st.session_state.agent_mode),
        )
        if st.button("会話リセット", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = None
    if not st.session_state.messages:
        selected = st.pills(
            "よく使う依頼",
            list(SUGGESTIONS.keys()),
            label_visibility="collapsed",
        )
        if selected:
            prompt = SUGGESTIONS[selected]

    chat_input = st.chat_input("メッセージを入力...")
    if not prompt and chat_input:
        prompt = chat_input.strip()

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                placeholder = st.empty()
                response = asyncio.run(
                    stream_text(
                        prompt,
                        st.session_state.agent_mode,
                        st.session_state.session_id,
                        placeholder,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                response = f"エラーが発生しました: {exc}"
                st.error(response)

        st.session_state.messages.append({"role": "assistant", "content": str(response)})
        st.rerun()


if __name__ == "__main__":
    main()
