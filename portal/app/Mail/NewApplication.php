<?php

namespace App\Mail;

use App\Models\JobApplication;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Address;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class NewApplication extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(public JobApplication $application) {}

    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'New job application: '.$this->application->position.' ('.$this->application->name.')',
            replyTo: [new Address($this->application->email, $this->application->name)],
        );
    }

    public function content(): Content
    {
        // The CV is not attached: it stays in the portal, behind the admin login
        return new Content(text: 'mail.new-application');
    }
}
