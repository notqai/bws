<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('job_applications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('vacancy_id')->nullable()->constrained()->nullOnDelete();
            $table->string('position');
            $table->string('name');
            $table->string('email');
            $table->string('phone');
            $table->string('location')->nullable();
            $table->unsignedTinyInteger('years_experience')->nullable();
            $table->text('message')->nullable();
            $table->string('cv_path');
            $table->string('cv_original_name');
            $table->unsignedInteger('cv_size');
            $table->string('status')->default('new')->index();
            $table->text('notes')->nullable();
            $table->timestamp('consented_at');
            $table->string('privacy_version');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('job_applications');
    }
};
