<?php

namespace App\Console\Commands;

use App\Models\JobApplication;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;

#[Signature('portal:prune-applications')]
#[Description('Delete job applications (and their CVs) older than the retention period')]
class PruneApplications extends Command
{
    public function handle(): int
    {
        $months = config('portal.retention_months');
        $count = 0;

        // One by one so each CV file is deleted with its record
        JobApplication::where('created_at', '<', now()->subMonths($months))
            ->lazyById()
            ->each(function (JobApplication $application) use (&$count) {
                $application->delete();
                $count++;
            });

        $this->info("Deleted {$count} application(s) older than {$months} months.");

        return self::SUCCESS;
    }
}
