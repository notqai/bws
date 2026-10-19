<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\JobApplication;
use App\Models\Vacancy;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Validation\Rule;
use Illuminate\View\View;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ApplicationController extends Controller
{
    public function index(Request $request): View
    {
        $filters = $request->only('status', 'vacancy', 'q');

        $applications = JobApplication::query()
            ->when($filters['status'] ?? null, fn ($q, $s) => $q->where('status', $s))
            ->when($filters['vacancy'] ?? null, fn ($q, $v) => $q->where('vacancy_id', $v))
            ->when($filters['q'] ?? null, fn ($q, $term) => $q->where(fn ($q) => $q
                ->where('name', 'like', "%{$term}%")
                ->orWhere('email', 'like', "%{$term}%")
                ->orWhere('position', 'like', "%{$term}%")))
            ->latest()
            ->paginate(25)
            ->withQueryString();

        return view('admin.applications.index', [
            'applications' => $applications,
            'filters' => $filters,
            'counts' => JobApplication::selectRaw('status, count(*) as n')->groupBy('status')->pluck('n', 'status'),
            'vacancies' => Vacancy::orderBy('title')->get(['id', 'title', 'location']),
        ]);
    }

    public function show(JobApplication $application): View
    {
        $application->load('vacancy');

        return view('admin.applications.show', compact('application'));
    }

    public function update(Request $request, JobApplication $application): RedirectResponse
    {
        $application->update($request->validate([
            'status' => ['required', Rule::in(array_keys(JobApplication::STATUSES))],
            'notes' => ['nullable', 'string', 'max:5000'],
        ]));

        return back()->with('status', 'Application updated.');
    }

    public function cv(JobApplication $application): StreamedResponse
    {
        abort_unless(Storage::disk(JobApplication::CV_DISK)->exists($application->cv_path), 404);

        return Storage::disk(JobApplication::CV_DISK)->download($application->cv_path, $application->cv_original_name);
    }

    public function destroy(JobApplication $application): RedirectResponse
    {
        $application->delete();

        return redirect()->route('admin.applications.index')->with('status', "Application from {$application->name} and the CV were deleted.");
    }
}
