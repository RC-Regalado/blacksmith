"""Package main entry point."""

import sys

from ai_assistant.bootstrap.container import create_application


def main() -> None:
    create_application().run(sys.argv[1:])


if __name__ == "__main__":
    main()
