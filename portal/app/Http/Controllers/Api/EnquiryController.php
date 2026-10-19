<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Mail\NewEnquiry;
use App\Models\Enquiry;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;

class EnquiryController extends Controller
{
    /** An enquiry from the website's Contact page. */
    public function store(Request $request): JsonResponse
    {
        // Spam honeypot: real visitors never see or fill this field. Pretend it worked.
        if (filled($request->input('_gotcha'))) {
            return response()->json(['ok' => true], 201);
        }

        $data = $request->validate([
            'name' => ['required', 'string', 'max:120'],
            'company' => ['nullable', 'string', 'max:160'],
            'email' => ['required', 'email', 'max:200'],
            'phone' => ['nullable', 'string', 'max:40'],
            'service' => ['nullable', 'string', 'max:120'],
            'message' => ['required', 'string', 'max:5000'],
        ]);

        $enquiry = Enquiry::create($data);

        try {
            Mail::to(config('portal.enquiry_email'))->send(new NewEnquiry($enquiry));
        } catch (\Throwable $e) {
            // The enquiry is saved and visible in the admin panel even if the email fails
            Log::warning('New enquiry email failed', ['enquiry' => $enquiry->id, 'error' => $e->getMessage()]);
        }

        return response()->json(['ok' => true], 201);
    }
}
