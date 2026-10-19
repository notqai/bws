<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\HseFigure;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class HseFigureController extends Controller
{
    public function index(): View
    {
        return view('admin.hse.index', ['figures' => HseFigure::orderBy('sort_order')->orderBy('id')->get()]);
    }

    public function create(): View
    {
        return view('admin.hse.form', ['figure' => new HseFigure(['as_of' => now()->startOfMonth(), 'is_published' => true])]);
    }

    public function store(Request $request): RedirectResponse
    {
        HseFigure::create($this->validated($request));

        return redirect()->route('admin.hse.index')->with('status', 'HSE figure saved.');
    }

    public function edit(HseFigure $hse): View
    {
        return view('admin.hse.form', ['figure' => $hse]);
    }

    public function update(Request $request, HseFigure $hse): RedirectResponse
    {
        $hse->update($this->validated($request));

        return redirect()->route('admin.hse.index')->with('status', 'HSE figure updated.');
    }

    public function destroy(HseFigure $hse): RedirectResponse
    {
        $hse->delete();

        return redirect()->route('admin.hse.index')->with('status', 'HSE figure deleted.');
    }

    private function validated(Request $request): array
    {
        $data = $request->validate([
            'value' => ['required', 'string', 'max:40'],
            'label' => ['required', 'string', 'max:120'],
            'detail' => ['nullable', 'string', 'max:200'],
            'as_of' => ['required', 'date', 'before_or_equal:today'],
            'sort_order' => ['nullable', 'integer', 'min:0', 'max:999'],
        ]);
        $data['sort_order'] = $data['sort_order'] ?? 0;
        $data['is_published'] = $request->boolean('is_published');

        return $data;
    }
}
