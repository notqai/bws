<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HseFigure;
use Illuminate\Http\JsonResponse;

class HseFigureController extends Controller
{
    /** Published HSE figures for the website's Home and HSE pages. */
    public function index(): JsonResponse
    {
        $figures = HseFigure::where('is_published', true)->orderBy('sort_order')->orderBy('id')->get()
            ->map(fn (HseFigure $f) => [
                'value' => $f->value,
                'label' => $f->label,
                'detail' => $f->detail,
                'as_of' => $f->as_of->toDateString(),
            ]);

        return response()->json(['ok' => true, 'figures' => $figures])
            ->header('Cache-Control', 'public, max-age=300');
    }
}
