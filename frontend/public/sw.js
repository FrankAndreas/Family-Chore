self.addEventListener('push', function (event) {
    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data = { title: event.data.text(), body: '' };
        }
    }

    const title = data.title || 'New Notification';
    const options = {
        body: data.body || '',
        icon: '/vite.svg', // Change to proper app icon
        badge: '/vite.svg',
        data: data.data || {}
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    // Focus or open app window
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
            if (windowClients.length > 0) {
                // Focus the first matching window
                windowClients[0].focus();
            } else {
                // Open a new window if none exists
                clients.openWindow('/');
            }
        })
    );
});
