<?php

use App\Http\Controllers\Admin\ApplicationController;
use App\Http\Controllers\Admin\AuthController;
use App\Http\Controllers\Admin\EnquiryController;
use App\Http\Controllers\Admin\HseFigureController;
use App\Http\Controllers\Admin\VacancyController;
use Illuminate\Support\Facades\Route;

Route::redirect('/', '/admin');

Route::middleware('guest')->group(function () {
    Route::get('/login', [AuthController::class, 'create'])->name('login');
    Route::post('/login', [AuthController::class, 'store'])->middleware('throttle:login');
});

Route::middleware('auth')->prefix('admin')->name('admin.')->group(function () {
    Route::redirect('/', '/admin/applications');
    Route::post('/logout', [AuthController::class, 'destroy'])->name('logout');

    Route::get('/applications', [ApplicationController::class, 'index'])->name('applications.index');
    Route::get('/applications/{application}', [ApplicationController::class, 'show'])->name('applications.show');
    Route::patch('/applications/{application}', [ApplicationController::class, 'update'])->name('applications.update');
    Route::get('/applications/{application}/cv', [ApplicationController::class, 'cv'])->name('applications.cv');
    Route::delete('/applications/{application}', [ApplicationController::class, 'destroy'])->name('applications.destroy');

    Route::get('/enquiries', [EnquiryController::class, 'index'])->name('enquiries.index');
    Route::get('/enquiries/{enquiry}', [EnquiryController::class, 'show'])->name('enquiries.show');
    Route::patch('/enquiries/{enquiry}', [EnquiryController::class, 'update'])->name('enquiries.update');
    Route::delete('/enquiries/{enquiry}', [EnquiryController::class, 'destroy'])->name('enquiries.destroy');

    Route::resource('vacancies', VacancyController::class)->except('show');
    Route::resource('hse', HseFigureController::class)->except('show')->parameters(['hse' => 'hse']);
});
