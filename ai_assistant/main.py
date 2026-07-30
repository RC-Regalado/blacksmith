"""Package main entry point."""

from ai_assistant.bootstrap.container import create_application


def main() -> None:
    create_application().run()


if __name__ == "__main__":
    main()
