function waitForFullscreenButton() {
    const interval = setInterval(() => {
        const btn = document.getElementById("fullscreen-btn");

        if (btn) {
            if (btn.dataset.fullscreenBound !== "true") {
                btn.addEventListener("click", () => {
                    const el = document.documentElement;

                    if (!document.fullscreenElement) {
                        el.requestFullscreen()
                            .then(() => {
                                console.log("Entered fullscreen");
                            })
                            .catch((err) => {
                                console.error("Failed to enter fullscreen:", err);
                            });
                    } else {
                        document.exitFullscreen()
                            .then(() => {
                                console.log("Exited fullscreen");
                            });
                    }
                });

                btn.dataset.fullscreenBound = "true";
                console.log("Fullscreen button initialized");
            }

            clearInterval(interval); // Detener la espera
        }
    }, 900); // Intenta cada 300ms
}

document.addEventListener("DOMContentLoaded", waitForFullscreenButton);
