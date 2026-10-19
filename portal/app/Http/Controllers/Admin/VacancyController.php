<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Vacancy;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class VacancyController extends Controller
{
    public function index(): View
    {
        $vacancies = Vacancy::withCount('applications')->latest()->get();

        return view('admin.vacancies.index', compact('vacancies'));
    }

    public function create(): View
    {
        return view('admin.vacancies.form', ['vacancy' => new Vacancy(['location' => 'Miri', 'employment_type' => 'Permanent'])]);
    }

    public function store(Request $request): RedirectResponse
    {
        $vacancy = Vacancy::create($this->validated($request));

        return redirect()->route('admin.vacancies.index')->with('status', "Vacancy \"{$vacancy->title}\" saved.");
    }

    public function edit(Vacancy $vacancy): View
    {
        return view('admin.vacancies.form', compact('vacancy'));
    }

    public function update(Request $request, Vacancy $vacancy): RedirectResponse
    {
        $vacancy->update($this->validated($request));

        return redirect()->route('admin.vacancies.index')->with('status', "Vacancy \"{$vacancy->title}\" updated.");
    }

    public function destroy(Vacancy $vacancy): RedirectResponse
    {
        // Applications are kept (vacancy_id becomes null); they still show the position applied for
        $vacancy->delete();

        return redirect()->route('admin.vacancies.index')->with('status', "Vacancy \"{$vacancy->title}\" deleted.");
    }

    private function validated(Request $request): array
    {
        $data = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'discipline' => ['nullable', 'string', 'max:120'],
            'location' => ['required', 'string', 'max:120'],
            'employment_type' => ['required', Rule::in(Vacancy::EMPLOYMENT_TYPES)],
            'summary' => ['required', 'string', 'max:2000'],
            'requirements' => ['nullable', 'string', 'max:4000'],
            'closes_on' => ['nullable', 'date'],
        ]);
        $data['is_published'] = $request->boolean('is_published');

        return $data;
    }
}
