<?php

use Illuminate\Support\Facades\Schedule;

// PDPA: applications and CVs are not kept longer than needed (see config/portal.php)
Schedule::command('portal:prune-applications')->daily();
