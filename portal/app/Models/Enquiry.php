<?php

namespace App\Models;

use Database\Factories\EnquiryFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['name', 'company', 'email', 'phone', 'service', 'message', 'status', 'notes'])]
class Enquiry extends Model
{
    /** @use HasFactory<EnquiryFactory> */
    use HasFactory;

    public const STATUSES = [
        'new' => 'New',
        'replied' => 'Replied',
        'quoted' => 'Quotation sent',
        'won' => 'Won',
        'lost' => 'Not awarded',
        'closed' => 'Closed',
    ];

    public function statusLabel(): string
    {
        return self::STATUSES[$this->status] ?? ucfirst($this->status);
    }
}
