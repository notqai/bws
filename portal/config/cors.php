<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Cross-Origin Resource Sharing (CORS) Configuration
    |--------------------------------------------------------------------------
    |
    | Here you may configure your settings for cross-origin resource sharing
    | or "CORS". This determines what cross-origin operations may execute
    | in web browsers. You are free to adjust these settings as needed.
    |
    | To learn more: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
    |
    */

    'paths' => ['api/*'],

    'allowed_methods' => ['GET', 'POST'],

    // Only the BWS website may call the API from a browser (PORTAL_SITE_ORIGINS in .env)
    // (parsed here as well as in config/portal.php: config files can't read each other while loading)
    'allowed_origins' => array_values(array_filter(array_map('trim', explode(',', env(
        'PORTAL_SITE_ORIGINS',
        'https://www.bwsengineeringsb.com,https://bwsengineeringsb.com'
    ))))),

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['Accept', 'Content-Type', 'X-Requested-With'],

    'exposed_headers' => [],

    'max_age' => 86400,

    'supports_credentials' => false,

];
