<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        RateLimiter::for('applications', fn (Request $request) => Limit::perHour(config('portal.applications_per_hour'))
            ->by($request->ip())
            ->response(fn () => response()->json(['ok' => false, 'error' => 'rate'], 429)));

        RateLimiter::for('enquiries', fn (Request $request) => Limit::perHour(config('portal.enquiries_per_hour'))
            ->by($request->ip())
            ->response(fn () => response()->json(['ok' => false, 'error' => 'rate'], 429)));

        RateLimiter::for('login', fn (Request $request) => Limit::perMinute(5)
            ->by(strtolower((string) $request->input('email')).'|'.$request->ip()));
    }
}
