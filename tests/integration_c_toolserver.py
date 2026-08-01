"""Manual integration check for Python framed client and C tool server."""

from test_c_toolserver_contract import (
    build_tool_request,
    decode_response,
    run_toolserver_request,
)


def main() -> None:
    response = run_toolserver_request(
        build_tool_request(
            request_id="integration-1",
            tool_name="read_file",
            workspace_id=".",
            args={"path": "README.md", "max_bytes": "16"},
        )
    )

    assert response[2] == 1
    assert response[3] == b"file read"
    assert b"bytes_read" in response[4]


if __name__ == "__main__":
    main()
