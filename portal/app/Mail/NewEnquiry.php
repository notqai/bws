<?php

namespace App\Mail;

use App\Models\Enquiry;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Address;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class NewEnquiry extends Mailable
{
    use Queueable, SerializesModels;

    public function __construct(public Enquiry $enquiry) {}

    public function envelope(): Envelope
    {
        $e = $this->enquiry;

        return new Envelope(
            subject: 'Website enquiry: '.($e->service ?: 'General').' ('.($e->company ?: $e->name).')',
            replyTo: [new Address($e->email, $e->name)],
        );
    }

    public function content(): Content
    {
        return new Content(text: 'mail.new-enquiry');
    }
}
