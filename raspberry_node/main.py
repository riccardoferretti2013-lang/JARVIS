from pathlib import Path

from jarvis_node import (
    JarvisNodeServer,
)


def main(
) -> None:

    root_path = (
        Path(__file__)
        .resolve()
        .parent
    )

    server = (
        JarvisNodeServer(
            root_path=root_path
        )
    )

    server.run()


if __name__ == "__main__":
    main()