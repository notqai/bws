<?php

namespace Tests\Feature;

use App\Mail\NewApplication;
use App\Models\JobApplication;
use App\Models\Vacancy;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class PublicApiTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        Storage::fake(JobApplication::CV_DISK);
        Mail::fake();
    }

    private function application(array $overrides = []): array
    {
        return array_merge([
            'position' => 'Rigger',
            'name' => 'Aminah binti Ali',
            'email' => 'aminah@example.com',
            'phone' => '012-345 6789',
            'years_experience' => 4,
            'cv' => UploadedFile::fake()->create('Aminah CV.pdf', 300, 'application/pdf'),
            'consent' => '1',
        ], $overrides);
    }

    public function test_lists_only_open_published_vacancies(): void
    {
        $open = Vacancy::factory()->create(['title' => 'Safety Officer', 'requirements' => "NIOSH SSS\n\nCIDB green card"]);
        Vacancy::factory()->create(['closes_on' => null, 'title' => 'Rigger']);
        Vacancy::factory()->draft()->create();
        Vacancy::factory()->closed()->create();

        $this->getJson('/api/vacancies')
            ->assertOk()
            ->assertJsonCount(2, 'vacancies')
            ->assertJsonPath('vacancies.0.title', 'Safety Officer')
            ->assertJsonPath('vacancies.0.requirements', ['NIOSH SSS', 'CIDB green card'])
            ->assertJsonPath('vacancies.0.id', $open->id);
    }

    public function test_cors_allows_only_the_website(): void
    {
        $this->getJson('/api/vacancies', ['Origin' => 'https://www.bwsengineeringsb.com'])
            ->assertHeader('Access-Control-Allow-Origin', 'https://www.bwsengineeringsb.com');

        $this->getJson('/api/vacancies', ['Origin' => 'https://evil.example'])
            ->assertHeaderMissing('Access-Control-Allow-Origin');
    }

    public function test_general_application_is_stored_privately_and_hr_is_emailed(): void
    {
        $this->post('/api/applications', $this->application(), ['Accept' => 'application/json'])
            ->assertCreated()->assertJson(['ok' => true]);

        $a = JobApplication::sole();
        $this->assertSame('Rigger', $a->position);
        $this->assertNull($a->vacancy_id);
        $this->assertSame('Aminah CV.pdf', $a->cv_original_name);
        $this->assertStringStartsWith('cvs/', $a->cv_path);
        $this->assertNotSame('cvs/Aminah CV.pdf', $a->cv_path);
        Storage::disk(JobApplication::CV_DISK)->assertExists($a->cv_path);
        $this->assertNotNull($a->consented_at);
        $this->assertSame(config('portal.privacy_version'), $a->privacy_version);

        Mail::assertSent(NewApplication::class, fn ($m) => $m->hasTo(config('portal.hr_email')) && $m->hasReplyTo('aminah@example.com'));
    }

    public function test_application_for_a_vacancy_takes_its_title(): void
    {
        $v = Vacancy::factory()->create(['title' => 'QA/QC Inspector']);

        $this->post('/api/applications', $this->application(['vacancy_id' => $v->id, 'position' => '']), ['Accept' => 'application/json'])
            ->assertCreated();

        $this->assertSame('QA/QC Inspector', JobApplication::sole()->position);
        $this->assertTrue(JobApplication::sole()->vacancy->is($v));
    }

    public function test_closed_or_draft_vacancies_cannot_be_applied_for(): void
    {
        $closed = Vacancy::factory()->closed()->create();
        $draft = Vacancy::factory()->draft()->create();

        $this->post('/api/applications', $this->application(['vacancy_id' => $closed->id]), ['Accept' => 'application/json'])
            ->assertStatus(422)->assertJson(['error' => 'closed']);
        $this->post('/api/applications', $this->application(['vacancy_id' => $draft->id]), ['Accept' => 'application/json'])
            ->assertStatus(422)->assertJsonValidationErrors('vacancy_id');

        $this->assertSame(0, JobApplication::count());
    }

    public function test_validation_consent_and_file_type(): void
    {
        $this->post('/api/applications', $this->application([
            'consent' => null,
            'email' => 'not-an-email',
            'cv' => UploadedFile::fake()->create('run-me.exe', 10, 'application/octet-stream'),
        ]), ['Accept' => 'application/json'])
            ->assertStatus(422)
            ->assertJsonValidationErrors(['consent', 'email', 'cv']);

        $this->post('/api/applications', $this->application([
            'cv' => UploadedFile::fake()->create('huge.pdf', config('portal.cv_max_kb') + 1, 'application/pdf'),
        ]), ['Accept' => 'application/json'])
            ->assertStatus(422)->assertJsonValidationErrors('cv');

        $this->assertSame(0, JobApplication::count());
        Mail::assertNothingSent();
    }

    public function test_honeypot_submissions_are_dropped_silently(): void
    {
        $this->post('/api/applications', $this->application(['_gotcha' => 'spam']), ['Accept' => 'application/json'])
            ->assertCreated();

        $this->assertSame(0, JobApplication::count());
        Mail::assertNothingSent();
    }

    public function test_applications_are_rate_limited_per_ip(): void
    {
        foreach (range(1, config('portal.applications_per_hour')) as $_) {
            $this->post('/api/applications', $this->application(), ['Accept' => 'application/json'])->assertCreated();
        }

        $this->post('/api/applications', $this->application(), ['Accept' => 'application/json'])
            ->assertStatus(429)->assertJson(['error' => 'rate']);
    }

    public function test_email_failure_does_not_lose_the_application(): void
    {
        Mail::shouldReceive('to')->andThrow(new \RuntimeException('SMTP down'));

        $this->post('/api/applications', $this->application(), ['Accept' => 'application/json'])->assertCreated();
        $this->assertSame(1, JobApplication::count());
    }
}
