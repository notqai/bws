<?php

namespace Database\Factories;

use App\Models\HseFigure;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<HseFigure>
 */
class HseFigureFactory extends Factory
{
    public function definition(): array
    {
        return [
            'value' => '1.2 million',
            'label' => 'Man-hours without LTI',
            'detail' => 'All active projects',
            'as_of' => now()->startOfMonth()->toDateString(),
            'sort_order' => 0,
            'is_published' => true,
        ];
    }
}
