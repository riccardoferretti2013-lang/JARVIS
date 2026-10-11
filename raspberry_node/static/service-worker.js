const CACHE_NAME =
    "jarvis-mobile-v1";


const STATIC_FILES = [
    "/",
    "/static/style.css",
    "/static/app.js",
    "/static/manifest.webmanifest",
    "/static/jarvis-icon.svg"
];


self.addEventListener(
    "install",
    event => {

        event.waitUntil(

            caches
                .open(
                    CACHE_NAME
                )
                .then(
                    cache => {

                        return cache.addAll(
                            STATIC_FILES
                        );

                    }
                )

        );

        self.skipWaiting();

    }
);


self.addEventListener(
    "activate",
    event => {

        event.waitUntil(

            caches
                .keys()
                .then(
                    cacheNames => {

                        return Promise.all(

                            cacheNames
                                .filter(
                                    cacheName =>
                                        cacheName !==
                                        CACHE_NAME
                                )
                                .map(
                                    cacheName =>
                                        caches.delete(
                                            cacheName
                                        )
                                )

                        );

                    }
                )

        );

        self.clients.claim();

    }
);


self.addEventListener(
    "fetch",
    event => {

        const request =
            event.request;

        const url =
            new URL(
                request.url
            );


        if (
            url.pathname.startsWith(
                "/api/"
            )
        ) {

            event.respondWith(
                fetch(
                    request
                )
            );

            return;

        }


        if (
            request.mode ===
            "navigate"
        ) {

            event.respondWith(

                fetch(
                    request
                )
                .then(
                    response => {

                        const copy =
                            response.clone();

                        caches
                            .open(
                                CACHE_NAME
                            )
                            .then(
                                cache => {

                                    cache.put(
                                        request,
                                        copy
                                    );

                                }
                            );

                        return response;

                    }
                )
                .catch(
                    () =>
                        caches.match(
                            "/"
                        )
                )

            );

            return;

        }


        event.respondWith(

            caches
                .match(
                    request
                )
                .then(
                    cachedResponse => {

                        if (
                            cachedResponse
                        ) {

                            return (
                                cachedResponse
                            );

                        }

                        return fetch(
                            request
                        );

                    }
                )

        );

    }
);