const statusElement =
    document.getElementById(
        "nodeStatus"
    );

const nodeNameElement =
    document.getElementById(
        "nodeName"
    );

const clockElement =
    document.getElementById(
        "clock"
    );

const dateElement =
    document.getElementById(
        "date"
    );

const remindersElement =
    document.getElementById(
        "reminders"
    );

const wakeButton =
    document.getElementById(
        "wakeButton"
    );

const wakeResult =
    document.getElementById(
        "wakeResult"
    );

const mainStatus =
    document.getElementById(
        "mainStatus"
    );

const workModeButton =
    document.getElementById(
        "workModeButton"
    );

const workModeResult =
    document.getElementById(
        "workModeResult"
    );

const commandResult =
    document.getElementById(
        "commandResult"
    );

const remoteCommandButtons =
    document.querySelectorAll(
        ".remote-command"
    );

const reminderForm =
    document.getElementById(
        "reminderForm"
    );

const reminderResult =
    document.getElementById(
        "reminderResult"
    );

const refreshButton =
    document.getElementById(
        "refreshButton"
    );

const pwaStatus =
    document.getElementById(
        "pwaStatus"
    );

const serviceWorkerStatus =
    document.getElementById(
        "serviceWorkerStatus"
    );

const appMode =
    document.getElementById(
        "appMode"
    );


function updateClock() {

    const now =
        new Date();

    clockElement.textContent =
        now.toLocaleTimeString(
            "it-IT",
            {
                hour: "2-digit",
                minute: "2-digit",
            }
        );

    dateElement.textContent =
        now.toLocaleDateString(
            "it-IT",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
            }
        );

}


function detectStandaloneMode() {

    const standalone =
        window.matchMedia(
            "(display-mode: standalone)"
        ).matches
        ||
        window.navigator.standalone === true;

    if (standalone) {

        appMode.textContent =
            "APP";

        pwaStatus.textContent =
            "INSTALLATA";

    } else {

        appMode.textContent =
            "WEB";

        pwaStatus.textContent =
            "WEB";

    }

}


async function registerServiceWorker() {

    if (
        !(
            "serviceWorker"
            in navigator
        )
    ) {

        serviceWorkerStatus.textContent =
            "NON SUPPORTATO";

        return;

    }

    try {

        await navigator
            .serviceWorker
            .register(
                "/static/service-worker.js"
            );

        serviceWorkerStatus.textContent =
            "ATTIVO";

        serviceWorkerStatus.classList.add(
            "cyan"
        );

    } catch (error) {

        console.error(
            "Service Worker:",
            error
        );

        serviceWorkerStatus.textContent =
            "NON ATTIVO";

    }

}


async function loadStatus() {

    try {

        const response =
            await fetch(
                "/api/status"
            );

        if (!response.ok) {

            throw new Error(
                "Node offline"
            );

        }

        const data =
            await response.json();

        nodeNameElement.textContent =
            data.node;

        statusElement.innerHTML =
            `
            <span class="status-dot"></span>
            ONLINE
            `;

        statusElement.classList.add(
            "online"
        );

    } catch {

        statusElement.innerHTML =
            `
            <span class="status-dot"></span>
            OFFLINE
            `;

        statusElement.classList.remove(
            "online"
        );

    }

}


async function loadMainStatus() {

    try {

        const response =
            await fetch(
                "/api/pc/status"
            );

        if (!response.ok) {

            throw new Error(
                "Errore controllo Main."
            );

        }

        const data =
            await response.json();

        if (data.ready) {

            mainStatus.textContent =
                "PRONTO";

            mainStatus.classList.add(
                "cyan"
            );

        } else {

            mainStatus.textContent =
                "NON DISPONIBILE";

            mainStatus.classList.remove(
                "cyan"
            );

        }

    } catch {

        mainStatus.textContent =
            "NON DISPONIBILE";

        mainStatus.classList.remove(
            "cyan"
        );

    }

}


async function sendRemoteCommand(
    command
) {

    const response =
        await fetch(
            "/api/pc/command",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body:
                    JSON.stringify(
                        {
                            command:
                                command,
                        }
                    ),
            }
        );

    const data =
        await response.json();

    if (!response.ok) {

        throw new Error(
            data.error
            ||
            "Errore comando."
        );

    }

    return data;

}


remoteCommandButtons.forEach(
    button => {

        button.addEventListener(
            "click",
            async () => {

                const command =
                    button.dataset.command;

                const label =
                    button.dataset.label;

                const dangerous =
                    button.classList.contains(
                        "dangerous-command"
                    );

                if (dangerous) {

                    const confirmed =
                        window.confirm(
                            `Confermi: ${label}?`
                        );

                    if (!confirmed) {
                        return;
                    }

                }

                const originalText =
                    button.textContent;

                button.disabled =
                    true;

                button.textContent =
                    "INVIO...";

                commandResult.textContent =
                    `Invio comando: ${label}...`;

                try {

                    await sendRemoteCommand(
                        command
                    );

                    commandResult.textContent =
                        `${label}: comando inviato.`;

                } catch (error) {

                    commandResult.textContent =
                        error.message;

                } finally {

                    setTimeout(
                        () => {

                            button.disabled =
                                false;

                            button.textContent =
                                originalText;

                        },
                        1000
                    );

                }

            }
        );

    }
);


wakeButton.addEventListener(
    "click",
    async () => {

        wakeButton.disabled =
            true;

        wakeResult.textContent =
            "Invio Wake-on-LAN...";

        try {

            const response =
                await fetch(
                    "/api/pc/wake",
                    {
                        method: "POST",
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.error
                    ||
                    "Errore."
                );

            }

            wakeResult.textContent =
                "Wake-on-LAN inviato.";

            mainStatus.textContent =
                "AVVIO...";

            mainStatus.classList.remove(
                "cyan"
            );

        } catch (error) {

            wakeResult.textContent =
                error.message;

        } finally {

            wakeButton.disabled =
                false;

        }

    }
);


workModeButton.addEventListener(
    "click",
    async () => {

        workModeButton.disabled =
            true;

        workModeButton.textContent =
            "PREPARAZIONE...";

        workModeResult.textContent =
            "J.A.R.V.I.S. sta preparando la postazione.";

        try {

            const response =
                await fetch(
                    "/api/pc/work-mode",
                    {
                        method: "POST",
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.error
                    ||
                    "Errore."
                );

            }

            workModeResult.textContent =
                data.message
                ||
                "Preparazione avviata.";

            mainStatus.textContent =
                "PREPARAZIONE";

            setTimeout(
                loadMainStatus,
                3000
            );

        } catch (error) {

            workModeResult.textContent =
                error.message;

        } finally {

            setTimeout(
                () => {

                    workModeButton.disabled =
                        false;

                    workModeButton.textContent =
                        "⚡ ATTIVA MODALITÀ LAVORO";

                },
                2000
            );

        }

    }
);


async function loadReminders() {

    remindersElement.innerHTML =
        `
        <p class="empty">
            Caricamento...
        </p>
        `;

    try {

        const response =
            await fetch(
                "/api/reminders"
            );

        if (!response.ok) {

            throw new Error(
                "Errore API"
            );

        }

        const reminders =
            await response.json();

        if (
            !Array.isArray(
                reminders
            )
            ||
            reminders.length === 0
        ) {

            remindersElement.innerHTML =
                `
                <p class="empty">
                    Nessun promemoria.
                </p>
                `;

            return;

        }

        remindersElement.innerHTML =
            "";

        for (
            const reminder
            of reminders
        ) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "reminder-item";

            const message =
                document.createElement(
                    "div"
                );

            message.className =
                "reminder-message";

            message.textContent =
                reminder.message;

            const time =
                document.createElement(
                    "div"
                );

            time.className =
                "reminder-time";

            const reminderDate =
                new Date(
                    reminder.remind_at
                );

            time.textContent =
                reminderDate
                    .toLocaleString(
                        "it-IT"
                    );

            item.appendChild(
                message
            );

            item.appendChild(
                time
            );

            remindersElement.appendChild(
                item
            );

        }

    } catch {

        remindersElement.innerHTML =
            `
            <p class="empty">
                Errore nel caricamento.
            </p>
            `;

    }

}


reminderForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        const message =
            document
                .getElementById(
                    "message"
                )
                .value
                .trim();

        const date =
            document
                .getElementById(
                    "reminderDate"
                )
                .value;

        const time =
            document
                .getElementById(
                    "reminderTime"
                )
                .value;

        if (
            !message
            ||
            !date
            ||
            !time
        ) {

            reminderResult.textContent =
                "Compila tutti i campi.";

            return;

        }

        const localDate =
            new Date(
                `${date}T${time}:00`
            );

        reminderResult.textContent =
            "Creazione...";

        try {

            const response =
                await fetch(
                    "/api/reminders",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                        },

                        body:
                            JSON.stringify(
                                {
                                    message:
                                        message,

                                    remind_at:
                                        localDate
                                            .toISOString(),
                                }
                            ),
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.error
                    ||
                    "Errore."
                );

            }

            reminderResult.textContent =
                "Promemoria creato.";

            reminderForm.reset();

            await loadReminders();

        } catch (error) {

            reminderResult.textContent =
                error.message;

        }

    }
);


refreshButton.addEventListener(
    "click",
    loadReminders
);


updateClock();

setInterval(
    updateClock,
    1000
);

detectStandaloneMode();

registerServiceWorker();

loadStatus();

loadMainStatus();

loadReminders();

setInterval(
    loadStatus,
    10000
);

setInterval(
    loadMainStatus,
    10000
);