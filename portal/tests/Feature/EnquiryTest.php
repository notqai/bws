<?php

namespace Tests\Feature;

use App\Mail\NewEnquiry;
use App\Models\Enquiry;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Mail;
use Tests\TestCase;

class EnquiryTest extends TestCase
{
    use RefreshDatabase;

    private array $form = [
        'name' => 'Ahmad Faiz',
        'company' => 'Acme Energy',
        'email' => 'faiz@acme.example',
        'phone' => '085-111222',
        'service' => 'Civil & Structural',
        'message' => 'Please quote for a 20 m pipe rack foundation.',
    ];

    public function test_enquiry_is_saved_and_emailed(): void
    {
        Mail::fake();

        $this->postJson('/api/enquiries', $this->form)->assertCreated()->assertJson(['ok' => true]);

        $e = Enquiry::sole();
        $this->assertSame('Acme Energy', $e->company);
        $this->assertSame('new', $e->status);
        Mail::assertSent(NewEnquiry::class, fn ($m) => $m->hasTo(config('portal.enquiry_email'))
            && $m->hasReplyTo('faiz@acme.example')
            && str_contains($m->envelope()->subject, 'Civil & Structural (Acme Energy)'));
    }

    public function test_validation_honeypot_and_rate_limit(): void
    {
        Mail::fake();

        $this->postJson('/api/enquiries', ['email' => 'nope'])->assertStatus(422)
            ->assertJsonValidationErrors(['name', 'email', 'message']);
        $this->postJson('/api/enquiries', $this->form + ['_gotcha' => 'bot'])->assertCreated();
        $this->assertSame(0, Enquiry::count());

        foreach (range(1, config('portal.enquiries_per_hour') - 2) as $_) {
            $this->postJson('/api/enquiries', $this->form)->assertCreated();
        }
        $this->postJson('/api/enquiries', $this->form)->assertStatus(429)->assertJson(['error' => 'rate']);
    }

    public function test_cors_preflight_from_the_website(): void
    {
        $this->call('OPTIONS', '/api/enquiries', [], [], [], [
            'HTTP_ORIGIN' => 'https://www.bwsengineeringsb.com',
            'HTTP_ACCESS_CONTROL_REQUEST_METHOD' => 'POST',
        ])->assertHeader('Access-Control-Allow-Origin', 'https://www.bwsengineeringsb.com');
    }

    public function test_admin_can_track_and_delete_enquiries(): void
    {
        $user = User::factory()->create();
        $won = Enquiry::factory()->create(['company' => 'Won Co', 'status' => 'won']);
        $new = Enquiry::factory()->create(['company' => 'Fresh Co']);

        $this->get('/admin/enquiries')->assertRedirect('/login');

        $this->actingAs($user)->get('/admin/enquiries')->assertOk()->assertSee('Won Co')->assertSee('Fresh Co');
        $this->actingAs($user)->get('/admin/enquiries?status=won')->assertSee('Won Co')->assertDontSee('Fresh Co');
        $this->actingAs($user)->get('/admin/enquiries?q=fresh')->assertSee('Fresh Co')->assertDontSee('Won Co');
        $this->actingAs($user)->get("/admin/enquiries/{$new->id}")->assertOk()->assertSee($new->message);

        $this->actingAs($user)->patch("/admin/enquiries/{$new->id}", ['status' => 'quoted', 'notes' => 'Q-2026-114'])->assertRedirect();
        $this->assertSame('quoted', $new->fresh()->status);
        $this->actingAs($user)->patch("/admin/enquiries/{$new->id}", ['status' => 'bogus'])->assertSessionHasErrors('status');

        $this->actingAs($user)->delete("/admin/enquiries/{$won->id}")->assertRedirect('/admin/enquiries');
        $this->assertModelMissing($won);
    }
}
