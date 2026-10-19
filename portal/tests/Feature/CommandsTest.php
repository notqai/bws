<?php

namespace Tests\Feature;

use App\Models\JobApplication;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class CommandsTest extends TestCase
{
    use RefreshDatabase;

    public function test_prune_deletes_old_applications_and_their_cvs(): void
    {
        Storage::fake(JobApplication::CV_DISK);
        $old = JobApplication::factory()->create(['cv_path' => 'cvs/old.pdf', 'created_at' => now()->subMonths(13)]);
        $recent = JobApplication::factory()->create(['cv_path' => 'cvs/new.pdf', 'created_at' => now()->subMonths(11)]);
        Storage::disk(JobApplication::CV_DISK)->put('cvs/old.pdf', 'x');
        Storage::disk(JobApplication::CV_DISK)->put('cvs/new.pdf', 'x');

        $this->artisan('portal:prune-applications')->expectsOutputToContain('Deleted 1 application')->assertSuccessful();

        $this->assertModelMissing($old);
        $this->assertModelExists($recent);
        Storage::disk(JobApplication::CV_DISK)->assertMissing('cvs/old.pdf');
        Storage::disk(JobApplication::CV_DISK)->assertExists('cvs/new.pdf');
    }

    public function test_create_and_reset_admin_user(): void
    {
        $this->artisan('portal:user', ['email' => 'HR@BWS.test', '--name' => 'HR'])
            ->expectsQuestion('Password (at least 12 characters)', 'short')
            ->assertFailed();
        $this->assertSame(0, User::count());

        $this->artisan('portal:user', ['email' => 'HR@BWS.test', '--name' => 'HR'])
            ->expectsQuestion('Password (at least 12 characters)', 'a long enough password')
            ->assertSuccessful();
        $this->artisan('portal:user', ['email' => 'hr@bws.test'])
            ->expectsQuestion('Password (at least 12 characters)', 'another long password')
            ->assertSuccessful();

        $user = User::sole();
        $this->assertSame('hr@bws.test', $user->email);
        $this->assertSame('HR', $user->name);
        $this->assertTrue(Hash::check('another long password', $user->password));
    }
}
