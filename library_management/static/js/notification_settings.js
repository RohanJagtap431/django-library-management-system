document.addEventListener("DOMContentLoaded", function () {

    const toneSelect = document.getElementById("notification-tone");
    const testButton = document.getElementById("test-tone-btn");

    if (toneSelect && testButton) {

        testButton.addEventListener("click", function () {
            const audio = new Audio(`/static/sounds/${toneSelect.value}.mp3`);
            audio.play();
        });

        const notification = document.querySelector('[data-notification="true"]');

        if (notification) {
            const audio = new Audio(`/static/sounds/${toneSelect.value}.mp3`);
            audio.play();
        }

    }

});
