A new enquiry has arrived through the website.

Name:     {{ $enquiry->name }}
Company:  {{ $enquiry->company ?: '-' }}
Email:    {{ $enquiry->email }}
Phone:    {{ $enquiry->phone ?: '-' }}
Service:  {{ $enquiry->service ?: '-' }}

{{ $enquiry->message }}

Track it in the portal (login required):
{{ route('admin.enquiries.show', $enquiry) }}

Replying to this email answers the sender directly.
