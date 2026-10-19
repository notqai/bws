<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Mail\NewApplication;
use App\Models\JobApplication;
use App\Models\Vacancy;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;
use Illuminate\Validation\Rule;

class ApplicationController extends Controller
{
    /** A job application with CV, sent from the website's Careers page. */
    public function store(Request $request): JsonResponse
    {
        // Spam honeypot: real visitors never see or fill this field. Pretend it worked.
        if (filled($request->input('_gotcha'))) {
            return response()->json(['ok' => true], 201);
        }

        $data = $request->validate([
            'vacancy_id' => ['nullable', 'integer', Rule::exists('vacancies', 'id')->where('is_published', true)],
            'position' => ['required_without:vacancy_id', 'nullable', 'string', 'max:120'],
            'name' => ['required', 'string', 'max:120'],
            'email' => ['required', 'email', 'max:200'],
            'phone' => ['required', 'string', 'max:40'],
            'location' => ['nullable', 'string', 'max:120'],
            'years_experience' => ['nullable', 'integer', 'min:0', 'max:60'],
            'message' => ['nullable', 'string', 'max:3000'],
            'cv' => ['required', 'file', 'mimes:pdf,doc,docx', 'max:'.config('portal.cv_max_kb')],
            'consent' => ['accepted'],
        ]);

        $vacancy = isset($data['vacancy_id']) ? Vacancy::find($data['vacancy_id']) : null;
        if ($vacancy && ! $vacancy->isOpen()) {
            return response()->json(['ok' => false, 'error' => 'closed'], 422);
        }

        $cv = $request->file('cv');
        $application = JobApplication::create([
            'vacancy_id' => $vacancy?->id,
            'position' => $vacancy?->title ?? $data['position'],
            'name' => $data['name'],
            'email' => $data['email'],
            'phone' => $data['phone'],
            'location' => $data['location'] ?? null,
            'years_experience' => $data['years_experience'] ?? null,
            'message' => $data['message'] ?? null,
            // Random file name in private storage; the original name is only used for downloads
            'cv_path' => $cv->store('cvs', JobApplication::CV_DISK),
            'cv_original_name' => mb_substr($cv->getClientOriginalName(), 0, 200),
            'cv_size' => $cv->getSize(),
            'consented_at' => now(),
            'privacy_version' => config('portal.privacy_version'),
        ]);

        try {
            Mail::to(config('portal.hr_email'))->send(new NewApplication($application));
        } catch (\Throwable $e) {
            // The application is saved and visible in the admin panel even if the email fails
            Log::warning('New application email failed', ['application' => $application->id, 'error' => $e->getMessage()]);
        }

        return response()->json(['ok' => true], 201);
    }
}
