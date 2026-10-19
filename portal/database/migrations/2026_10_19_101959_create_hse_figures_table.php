<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('hse_figures', function (Blueprint $table) {
            $table->id();
            $table->string('value');
            $table->string('label');
            $table->string('detail')->nullable();
            $table->date('as_of');
            $table->unsignedSmallInteger('sort_order')->default(0);
            $table->boolean('is_published')->default(false);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('hse_figures');
    }
};
