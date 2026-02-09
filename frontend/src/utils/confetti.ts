import confetti from 'canvas-confetti';

export const triggerConfetti = () => {
    const duration = 3 * 1000;
    const end = Date.now() + duration;

    (function frame() {
        confetti({
            particleCount: 5,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: ['#cd7f32', '#c0c0c0', '#ffd700'], // Bronze, Silver, Gold colors
        });
        confetti({
            particleCount: 5,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: ['#cd7f32', '#c0c0c0', '#ffd700'],
        });

        if (Date.now() < end) {
            requestAnimationFrame(frame);
        }
    })();
};
