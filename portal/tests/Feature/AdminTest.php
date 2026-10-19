<?php

namespace Tests\Feature;

use App\Models\JobApplication;
use App\Models\User;
use App\Models\Vacancy;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class AdminTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        Storage::fake(JobApplication::CV_DISK);
    }

    public function test_admin_pages_need_a_login(): void
    {
        $a = JobApplication::factory()->create();

        foreach (['/admin/applications', "/admin/applications/{$a->id}", "/admin/applications/{$a->id}/cv", '/admin/vacancies'] as $url) {
            $this->get($url)->assertRedirect('/login');
        }
        $this->delete("/admin/applications/{$a->id}")->assertRedirect('/login');
        $this->assertModelExists($a);
    }

    public function test_login_and_logout(): void
    {
        $user = User::factory()->create(['email' => 'hr@bws.test', 'password' => 'correct horse battery']);

        $this->post('/login', ['email' => 'hr@bws.test', 'password' => 'wrong'])->assertSessionHasErrors('email');
        $this->assertGuest();

        $this->post('/login', ['email' => 'hr@bws.test', 'password' => 'correct horse battery'])
            ->assertRedirect(route('admin.applications.index'));
        $this->assertAuthenticatedAs($user);

        $this->post('/admin/logout')->assertRedirect('/login');
        $this->assertGuest();
    }

    public function test_login_is_throttled(): void
    {
        User::factory()->create(['email' => 'hr@bws.test']);
        foreach (range(1, 5) as $_) {
            $this->post('/login', ['email' => 'hr@bws.test', 'password' => 'nope']);
        }
        $this->post('/login', ['email' => 'hr@bws.test', 'password' => 'nope'])->assertStatus(429);
    }

    public function test_list_filter_view_and_update_applications(): void
    {
        $user = User::factory()->create();
        $v = Vacancy::factory()->create(['title' => 'Site Engineer']);
        $mine = JobApplication::factory()->create(['vacancy_id' => $v->id, 'position' => 'Site Engineer', 'name' => 'Lim Wei Jie']);
        JobApplication::factory()->create(['name' => 'Someone Else', 'status' => 'rejected']);

        $this->actingAs($user)->get('/admin/applications')->assertOk()->assertSee('Lim Wei Jie')->assertSee('Someone Else')
            ->assertHeader('Cache-Control', 'no-store, private');
        $this->actingAs($user)->get('/admin/applications?status=new')->assertSee('Lim Wei Jie')->assertDontSee('Someone Else');
        $this->actingAs($user)->get("/admin/applications?vacancy={$v->id}")->assertSee('Lim Wei Jie')->assertDontSee('Someone Else');
        $this->actingAs($user)->get('/admin/applications?q=else')->assertSee('Someone Else')->assertDontSee('Lim Wei Jie');

        $this->actingAs($user)->get("/admin/applications/{$mine->id}")->assertOk()->assertSee('Download CV');

        $this->actingAs($user)->patch("/admin/applications/{$mine->id}", ['status' => 'shortlisted', 'notes' => 'Call Monday'])
            ->assertRedirect();
        $this->assertSame('shortlisted', $mine->fresh()->status);
        $this->assertSame('Call Monday', $mine->fresh()->notes);

        $this->actingAs($user)->patch("/admin/applications/{$mine->id}", ['status' => 'bogus'])->assertSessionHasErrors('status');
    }

    public function test_cv_download_and_delete_removes_the_file(): void
    {
        $user = User::factory()->create();
        $a = JobApplication::factory()->create(['cv_path' => 'cvs/abc.pdf', 'cv_original_name' => 'Ali CV.pdf']);
        Storage::disk(JobApplication::CV_DISK)->put('cvs/abc.pdf', '%PDF-1.4 test');

        $this->actingAs($user)->get("/admin/applications/{$a->id}/cv")
            ->assertOk()->assertDownload('Ali CV.pdf');

        $this->actingAs($user)->delete("/admin/applications/{$a->id}")->assertRedirect(route('admin.applications.index'));
        $this->assertModelMissing($a);
        Storage::disk(JobApplication::CV_DISK)->assertMissing('cvs/abc.pdf');
    }

    public function test_vacancy_crud(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)->post('/admin/vacancies', [
            'title' => 'Scaffolder', 'location' => 'Bintulu', 'employment_type' => 'Contract',
            'summary' => 'Erect and dismantle scaffolding.', 'is_published' => '1',
        ])->assertRedirect('/admin/vacancies');
        $v = Vacancy::sole();
        $this->assertTrue($v->is_published);
        $this->getJson('/api/vacancies')->assertJsonPath('vacancies.0.title', 'Scaffolder');

        $this->actingAs($user)->put("/admin/vacancies/{$v->id}", [
            'title' => 'Scaffolder', 'location' => 'Bintulu', 'employment_type' => 'Contract', 'summary' => 'Updated.',
        ])->assertRedirect('/admin/vacancies');
        $this->assertFalse($v->fresh()->is_published); // unticked checkbox unpublishes
        $this->getJson('/api/vacancies')->assertJsonCount(0, 'vacancies');

        $this->actingAs($user)->post('/admin/vacancies', ['title' => '', 'employment_type' => 'Freelance'])
            ->assertSessionHasErrors(['title', 'location', 'summary', 'employment_type']);

        $app = JobApplication::factory()->create(['vacancy_id' => $v->id]);
        $this->actingAs($user)->delete("/admin/vacancies/{$v->id}")->assertRedirect('/admin/vacancies');
        $this->assertModelMissing($v);
        $this->assertNull($app->fresh()->vacancy_id);

        $this->actingAs($user)->get('/admin/vacancies')->assertOk();
        $this->actingAs($user)->get('/admin/vacancies/create')->assertOk();
    }
}
