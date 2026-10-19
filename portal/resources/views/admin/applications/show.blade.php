@extends('admin.layout')
@section('title', $application->name)
@section('content')
<p><a href="{{ route('admin.applications.index') }}">&larr; All applications</a></p>
<div class="head">
  <h1>{{ $application->name }}</h1>
  <p class="muted">Applied for <strong>{{ $application->position }}</strong> on {{ $application->created_at->timezone('Asia/Kuching')->format('j M Y, g:i a') }}</p>
</div>

<div class="grid">
  <section class="card">
    <h2>Details</h2>
    <dl class="details">
      <dt>Email</dt><dd><a href="mailto:{{ $application->email }}">{{ $application->email }}</a></dd>
      <dt>Phone</dt><dd><a href="tel:{{ preg_replace('/[^0-9+]/', '', $application->phone) }}">{{ $application->phone }}</a></dd>
      <dt>Location</dt><dd>{{ $application->location ?: '-' }}</dd>
      <dt>Experience</dt><dd>{{ $application->years_experience !== null ? $application->years_experience.' years' : '-' }}</dd>
      <dt>Vacancy</dt><dd>@if ($application->vacancy)<a href="{{ route('admin.vacancies.edit', $application->vacancy) }}">{{ $application->vacancy->title }} ({{ $application->vacancy->location }})</a>@else General application @endif</dd>
      <dt>Consent</dt><dd>Agreed to privacy notice {{ $application->privacy_version }} on {{ $application->consented_at->timezone('Asia/Kuching')->format('j M Y') }}</dd>
    </dl>
    <h3>Message</h3>
    <p class="message">{{ $application->message ?: 'No message.' }}</p>
    <p><a class="btn" href="{{ route('admin.applications.cv', $application) }}">Download CV</a> <span class="muted small">{{ $application->cv_original_name }} &middot; {{ number_format($application->cv_size / 1024) }} KB</span></p>
  </section>

  <section class="card">
    <h2>Progress</h2>
    <form method="POST" action="{{ route('admin.applications.update', $application) }}" class="stack">
      @csrf @method('PATCH')
      <label>Status
        <select name="status">
          @foreach (\App\Models\JobApplication::STATUSES as $key => $label)
            <option value="{{ $key }}" @selected($application->status === $key)>{{ $label }}</option>
          @endforeach
        </select>
      </label>
      <label>Internal notes <textarea name="notes" rows="6" placeholder="Not shown to the applicant">{{ old('notes', $application->notes) }}</textarea></label>
      <button class="btn" type="submit">Save</button>
    </form>

    <form method="POST" action="{{ route('admin.applications.destroy', $application) }}" class="danger-zone" data-confirm="Delete this application and the CV permanently?">
      @csrf @method('DELETE')
      <p class="muted small">Delete when the applicant asks you to, or when it is no longer needed.</p>
      <button class="btn btn--danger" type="submit">Delete application and CV</button>
    </form>
  </section>
</div>
<script src="{{ asset('js/admin.js') }}"></script>
@endsection
