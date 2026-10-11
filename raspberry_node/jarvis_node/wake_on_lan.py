import socket


class WakeOnLan:

    @staticmethod
    def wake(
        mac_address: str,
    ) -> None:

        clean_mac = (
            mac_address
            .replace(
                ":",
                "",
            )
            .replace(
                "-",
                "",
            )
            .replace(
                ".",
                "",
            )
            .strip()
        )

        if len(clean_mac) != 12:

            raise ValueError(
                "MAC address non valido."
            )

        try:

            mac_bytes = (
                bytes.fromhex(
                    clean_mac
                )
            )

        except ValueError as exc:

            raise ValueError(
                "MAC address non valido."
            ) from exc

        packet = (
            b"\xff" * 6
            + mac_bytes * 16
        )

        with socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        ) as sock:

            sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_BROADCAST,
                1,
            )

            sock.sendto(
                packet,
                (
                    "255.255.255.255",
                    9,
                ),
            )