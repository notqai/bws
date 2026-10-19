<?php

use App\Http\Controllers\Api\ApplicationController;
use App\Http\Controllers\Api\EnquiryController;
use App\Http\Controllers\Api\HseFigureController;
use App\Http\Controllers\Api\VacancyController;
use Illuminate\Support\Facades\Route;

// Called from the static website (Careers page); CORS origins are set in config/portal.php
Route::get('/vacancies', [VacancyController::class, 'index']);
Route::post('/applications', [ApplicationController::class, 'store'])->middleware('throttle:applications');
Route::post('/enquiries', [EnquiryController::class, 'store'])->middleware('throttle:enquiries');
Route::get('/hse-figures', [HseFigureController::class, 'index']);
