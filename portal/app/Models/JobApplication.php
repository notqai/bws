<?php

namespace App\Models;

use Database\Factories\JobApplicationFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Storage;

#[Fillable([
    'vacancy_id', 'position', 'name', 'email', 'phone', 'location', 'years_experience', 'message',
    'cv_path', 'cv_original_name', 'cv_size', 'status', 'notes', 'consented_at', 'privacy_version',
])]
class JobApplication extends Model
{
    /** @use HasFactory<JobApplicationFactory> */
    use HasFactory;

    public const STATUSES = [
        'new' => 'New',
        'reviewing' => 'Reviewing',
        'shortlisted' => 'Shortlisted',
        'interview' => 'Interview',
        'hired' => 'Hired',
        'rejected' => 'Not suitable',
    ];

    public const CV_DISK = 'local';

    protected function casts(): array
    {
        return [
            'consented_at' => 'datetime',
            'years_experience' => 'integer',
            'cv_size' => 'integer',
        ];
    }

    protected static function booted(): void
    {
        // The CV goes with the record, so deleting an application never leaves personal data behind
        static::deleted(fn (JobApplication $a) => Storage::disk(self::CV_DISK)->delete($a->cv_path));
    }

    public function vacancy(): BelongsTo
    {
        return $this->belongsTo(Vacancy::class);
    }

    public function statusLabel(): string
    {
        return self::STATUSES[$this->status] ?? ucfirst($this->status);
    }
}
