<?php

return [

    // Inbox that receives each new website enquiry
    'enquiry_email' => env('PORTAL_ENQUIRY_EMAIL', 'bws@bwsengineeringsb.com'),

    // Inbox that is told about each new job application
    'hr_email' => env('PORTAL_HR_EMAIL', 'bwsesbhr@gmail.com'),

    // Website origins allowed to call the public API (comma separated)
    'site_origins' => array_values(array_filter(array_map('trim', explode(',', env(
        'PORTAL_SITE_ORIGINS',
        'https://www.bwsengineeringsb.com,https://bwsengineeringsb.com'
    ))))),

    // Applications (and their CVs) are deleted automatically after this many months (PDPA retention)
    'retention_months' => (int) env('PORTAL_RETENTION_MONTHS', 12),

    // Version of the privacy notice applicants agree to; bump it when privacy.html changes
    'privacy_version' => env('PORTAL_PRIVACY_VERSION', '2026-10'),

    // Largest CV upload, in kilobytes
    'cv_max_kb' => 5120,

    // Applications accepted per visitor IP per hour
    'applications_per_hour' => 5,

    // Enquiries accepted per visitor IP per hour
    'enquiries_per_hour' => 5,

];
