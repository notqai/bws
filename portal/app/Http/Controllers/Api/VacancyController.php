<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Vacancy;
use Illuminate\Http\JsonResponse;

class VacancyController extends Controller
{
    /** Open vacancies for the website's Careers page. */
    public function index(): JsonResponse
    {
        $vacancies = Vacancy::open()->orderByRaw('closes_on is null, closes_on')->orderBy('title')->get()
            ->map(fn (Vacancy $v) => [
                'id' => $v->id,
                'title' => $v->title,
                'discipline' => $v->discipline,
                'location' => $v->location,
                'employment_type' => $v->employment_type,
                'summary' => $v->summary,
                'requirements' => $v->requirements ? array_values(array_filter(array_map('trim', explode("\n", $v->requirements)))) : [],
                'closes_on' => $v->closes_on?->toDateString(),
            ]);

        return response()->json(['ok' => true, 'vacancies' => $vacancies])
            ->header('Cache-Control', 'public, max-age=300');
    }
}
