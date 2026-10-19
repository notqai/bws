<?php
/*
 * Enquiry form handler for cPanel / Apache hosting (PHP 7.4+).
 * contact.html posts here in the background and reads the JSON reply.
 * On hosts without PHP (Vercel, Netlify) the POST fails and the form falls back to a
 * pre-filled email instead, so nothing breaks there.
 *
 * Settings: change the three addresses below if needed.
 */

const TO_EMAIL   = 'bws@bwsengineeringsb.com';      // where enquiries are delivered
const FROM_EMAIL = 'website@bwsengineeringsb.com';  // must be an address on this domain, or many inboxes treat it as spam
const CC_EMAIL   = '';                              // optional second inbox, e.g. 'bwsesb@gmail.com'
const MAX_PER_HOUR = 5;                             // submissions allowed per visitor IP per hour

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function reply(int $status, array $body): void {
    http_response_code($status);
    echo json_encode($body);
    exit;
}

function field(string $name, int $max): string {
    $v = isset($_POST[$name]) && is_string($_POST[$name]) ? trim($_POST[$name]) : '';
    return function_exists('mb_substr') ? mb_substr($v, 0, $max, 'UTF-8') : substr($v, 0, $max);
}

function one_line(string $v): string {
    return trim(preg_replace('/[\r\n\t]+/', ' ', $v));  // stops header injection via name / subject
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    reply(405, ['ok' => false, 'error' => 'method']);
}

// Spam honeypot: real visitors never see or fill this field. Pretend it worked.
if (field('_gotcha', 200) !== '') {
    reply(200, ['ok' => true]);
}

$name    = one_line(field('name', 120));
$company = one_line(field('company', 160));
$email   = one_line(field('email', 200));
$phone   = one_line(field('phone', 40));
$service = one_line(field('service', 120));
$message = field('message', 5000);

$invalid = [];
if ($name === '') $invalid[] = 'name';
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) $invalid[] = 'email';
if ($message === '') $invalid[] = 'message';
if ($invalid) {
    reply(422, ['ok' => false, 'error' => 'invalid', 'fields' => $invalid]);
}

// Simple per-IP rate limit, stored in the server's temp folder
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$rate_file = sys_get_temp_dir() . '/bws-enquiry-' . hash('sha256', $ip . __FILE__);
$now = time();
$hits = [];
if (is_readable($rate_file)) {
    $hits = array_filter(array_map('intval', explode("\n", (string) file_get_contents($rate_file))),
        function ($t) use ($now) { return $t > $now - 3600; });
}
if (count($hits) >= MAX_PER_HOUR) {
    reply(429, ['ok' => false, 'error' => 'rate']);
}

$subject = 'Website enquiry: ' . ($service !== '' ? $service : 'General') . ' (' . ($company !== '' ? $company : $name) . ')';
$body = implode("\n", [
    'Name: ' . $name,
    'Company: ' . ($company !== '' ? $company : '-'),
    'Email: ' . $email,
    'Phone: ' . ($phone !== '' ? $phone : '-'),
    'Service of interest: ' . ($service !== '' ? $service : '-'),
    '',
    $message,
    '',
    '--',
    'Sent from the enquiry form on ' . ($_SERVER['HTTP_HOST'] ?? 'the website') . ' on ' . gmdate('j M Y, H:i') . ' UTC.',
    'Reply to this email to answer the sender directly.',
]);

$headers = [
    'From: BWS Website <' . FROM_EMAIL . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];
if (CC_EMAIL !== '') $headers[] = 'Cc: ' . CC_EMAIL;

$sent = mail(TO_EMAIL, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, implode("\r\n", $headers), '-f' . FROM_EMAIL);
if (!$sent) {
    reply(500, ['ok' => false, 'error' => 'send']);
}

$hits[] = $now;
@file_put_contents($rate_file, implode("\n", $hits), LOCK_EX);
reply(200, ['ok' => true]);
