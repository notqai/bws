A new job application has arrived through the website.

Position:   {{ $application->position }}
Name:       {{ $application->name }}
Email:      {{ $application->email }}
Phone:      {{ $application->phone }}
Location:   {{ $application->location ?: '-' }}
Experience: {{ $application->years_experience !== null ? $application->years_experience.' years' : '-' }}

{{ $application->message ?: '(No message)' }}

View the application and download the CV (login required):
{{ route('admin.applications.show', $application) }}

Replying to this email answers the applicant directly.
