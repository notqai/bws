<?php

namespace Database\Factories;

use App\Models\JobApplication;
use App\Models\Vacancy;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends Factory<JobApplication>
 */
class JobApplicationFactory extends Factory
{
    public function definition(): array
    {
        return [
            'vacancy_id' => Vacancy::factory(),
            'position' => 'Piping Supervisor',
            'name' => fake()->name(),
            'email' => fake()->safeEmail(),
            'phone' => '012-345 6789',
            'location' => 'Miri',
            'years_experience' => 5,
            'message' => fake()->sentence(),
            'cv_path' => 'cvs/'.Str::random(40).'.pdf',
            'cv_original_name' => 'cv.pdf',
            'cv_size' => 120_000,
            'status' => 'new',
            'consented_at' => now(),
            'privacy_version' => config('portal.privacy_version'),
        ];
    }
}
