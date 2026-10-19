<?php

namespace Tests\Feature;

use App\Models\HseFigure;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class HseFigureTest extends TestCase
{
    use RefreshDatabase;

    public function test_api_lists_published_figures_in_order(): void
    {
        HseFigure::factory()->create(['value' => 'Zero', 'label' => 'Lost-time injuries', 'sort_order' => 2]);
        HseFigure::factory()->create(['value' => '1.2 million', 'label' => 'Man-hours', 'sort_order' => 1, 'as_of' => '2026-10-01']);
        HseFigure::factory()->create(['value' => 'Hidden', 'is_published' => false]);

        $this->getJson('/api/hse-figures')->assertOk()
            ->assertJsonCount(2, 'figures')
            ->assertJsonPath('figures.0.value', '1.2 million')
            ->assertJsonPath('figures.0.as_of', '2026-10-01')
            ->assertJsonPath('figures.1.value', 'Zero')
            ->assertHeader('Cache-Control', 'max-age=300, public');
    }

    public function test_admin_crud(): void
    {
        $user = User::factory()->create();
        $this->get('/admin/hse')->assertRedirect('/login');

        $this->actingAs($user)->post('/admin/hse', [
            'value' => '2.1 million', 'label' => 'Man-hours without LTI', 'as_of' => now()->toDateString(), 'is_published' => '1',
        ])->assertRedirect('/admin/hse');
        $f = HseFigure::sole();
        $this->assertTrue($f->is_published);
        $this->assertSame(0, $f->sort_order);

        $this->actingAs($user)->post('/admin/hse', ['value' => '', 'label' => '', 'as_of' => now()->addMonth()->toDateString()])
            ->assertSessionHasErrors(['value', 'label', 'as_of']);

        $this->actingAs($user)->put("/admin/hse/{$f->id}", [
            'value' => '2.2 million', 'label' => 'Man-hours without LTI', 'as_of' => now()->toDateString(),
        ])->assertRedirect('/admin/hse');
        $this->assertSame('2.2 million', $f->fresh()->value);
        $this->assertFalse($f->fresh()->is_published);

        $this->actingAs($user)->get('/admin/hse')->assertOk()->assertSee('2.2 million');
        $this->actingAs($user)->get("/admin/hse/{$f->id}/edit")->assertOk();
        $this->actingAs($user)->get('/admin/hse/create')->assertOk();
        $this->actingAs($user)->delete("/admin/hse/{$f->id}")->assertRedirect('/admin/hse');
        $this->assertModelMissing($f);
    }
}
