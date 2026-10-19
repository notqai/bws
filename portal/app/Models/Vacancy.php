<?php

namespace App\Models;

use Database\Factories\VacancyFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['title', 'discipline', 'location', 'employment_type', 'summary', 'requirements', 'closes_on', 'is_published'])]
class Vacancy extends Model
{
    /** @use HasFactory<VacancyFactory> */
    use HasFactory;

    public const EMPLOYMENT_TYPES = ['Permanent', 'Contract', 'Project-based', 'Internship'];

    protected function casts(): array
    {
        return [
            'closes_on' => 'date',
            'is_published' => 'boolean',
        ];
    }

    public function applications(): HasMany
    {
        return $this->hasMany(JobApplication::class);
    }

    /** Published and not past its closing date: what the website shows. */
    public function scopeOpen(Builder $query): void
    {
        $query->where('is_published', true)
            ->where(fn (Builder $q) => $q->whereNull('closes_on')->orWhereDate('closes_on', '>=', today()));
    }

    public function isOpen(): bool
    {
        return $this->is_published && (! $this->closes_on || $this->closes_on->gte(today()));
    }
}
