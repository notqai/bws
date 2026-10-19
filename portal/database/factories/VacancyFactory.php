<?php

namespace Database\Factories;

use App\Models\Vacancy;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Vacancy>
 */
class VacancyFactory extends Factory
{
    public function definition(): array
    {
        return [
            'title' => fake()->randomElement(['Piping Supervisor', 'Safety Officer', 'QA/QC Inspector', 'Rigger', 'Site Engineer']),
            'discipline' => fake()->randomElement(['Mechanical & Piping', 'HSE', 'Civil & Structural', null]),
            'location' => fake()->randomElement(['Miri', 'Bintulu']),
            'employment_type' => 'Contract',
            'summary' => fake()->sentence(12),
            'requirements' => "Diploma or degree in a related field\nAt least 3 years' oil and gas experience",
            'closes_on' => now()->addMonth()->toDateString(),
            'is_published' => true,
        ];
    }

    public function draft(): static
    {
        return $this->state(['is_published' => false]);
    }

    public function closed(): static
    {
        return $this->state(['closes_on' => now()->subDay()->toDateString()]);
    }
}
