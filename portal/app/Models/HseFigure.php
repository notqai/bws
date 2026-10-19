<?php

namespace App\Models;

use Database\Factories\HseFigureFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/** A headline HSE figure (e.g. "2.1 million" / "man-hours without LTI") shown on the website. */
#[Fillable(['value', 'label', 'detail', 'as_of', 'sort_order', 'is_published'])]
class HseFigure extends Model
{
    /** @use HasFactory<HseFigureFactory> */
    use HasFactory;

    protected function casts(): array
    {
        return [
            'as_of' => 'date',
            'sort_order' => 'integer',
            'is_published' => 'boolean',
        ];
    }
}
