<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Validator;

#[Signature('portal:user {email : Login email} {--name= : Display name}')]
#[Description('Create an admin login, or reset the password of an existing one')]
class CreateAdminUser extends Command
{
    public function handle(): int
    {
        $email = strtolower($this->argument('email'));
        $password = $this->secret('Password (at least 12 characters)');

        $validator = Validator::make(['email' => $email, 'password' => $password], [
            'email' => ['required', 'email'],
            'password' => ['required', 'string', 'min:12'],
        ]);
        if ($validator->fails()) {
            foreach ($validator->errors()->all() as $error) {
                $this->error($error);
            }

            return self::FAILURE;
        }

        $user = User::updateOrCreate(
            ['email' => $email],
            ['name' => $this->option('name') ?: User::where('email', $email)->value('name') ?: $email, 'password' => $password],
        );

        $this->info(($user->wasRecentlyCreated ? 'Created' : 'Updated').' admin login for '.$email.'.');

        return self::SUCCESS;
    }
}
