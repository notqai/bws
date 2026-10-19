@extends('admin.layout')
@section('title', $vacancy->exists ? 'Edit vacancy' : 'Add vacancy')
@section('content')
<p><a href="{{ route('admin.vacancies.index') }}">&larr; All vacancies</a></p>
<div class="card">
  <h1>{{ $vacancy->exists ? 'Edit vacancy' : 'Add vacancy' }}</h1>
  @if ($errors->any())<p class="error" role="alert">Please check the highlighted fields.</p>@endif
  <form method="POST" action="{{ $vacancy->exists ? route('admin.vacancies.update', $vacancy) : route('admin.vacancies.store') }}" class="stack">
    @csrf
    @if ($vacancy->exists) @method('PUT') @endif
    <div class="row">
      <label>Position title <input name="title" value="{{ old('title', $vacancy->title) }}" required maxlength="120">@error('title')<span class="error">{{ $message }}</span>@enderror</label>
      <label>Discipline <input name="discipline" value="{{ old('discipline', $vacancy->discipline) }}" maxlength="120" placeholder="e.g. Mechanical &amp; Piping" list="disciplines"></label>
      <datalist id="disciplines"><option>Plant Construction &amp; Maintenance</option><option>Mechanical &amp; Piping</option><option>Civil &amp; Structural</option><option>Electrical &amp; Instrumentation</option><option>HSE</option><option>Office &amp; Administration</option></datalist>
    </div>
    <div class="row">
      <label>Location <input name="location" value="{{ old('location', $vacancy->location) }}" required maxlength="120" list="locations">@error('location')<span class="error">{{ $message }}</span>@enderror</label>
      <datalist id="locations"><option>Miri</option><option>Bintulu</option><option>Miri / Bintulu</option><option>Offshore</option></datalist>
      <label>Type
        <select name="employment_type">
          @foreach (\App\Models\Vacancy::EMPLOYMENT_TYPES as $t)<option @selected(old('employment_type', $vacancy->employment_type) === $t)>{{ $t }}</option>@endforeach
        </select>
      </label>
      <label>Closing date <input type="date" name="closes_on" value="{{ old('closes_on', $vacancy->closes_on?->toDateString()) }}"><span class="muted small">Leave empty to keep it open</span></label>
    </div>
    <label>Summary <textarea name="summary" rows="3" required maxlength="2000">{{ old('summary', $vacancy->summary) }}</textarea>@error('summary')<span class="error">{{ $message }}</span>@enderror</label>
    <label>Requirements <span class="muted small">(one per line)</span><textarea name="requirements" rows="6" maxlength="4000">{{ old('requirements', $vacancy->requirements) }}</textarea></label>
    <label class="check"><input type="checkbox" name="is_published" value="1" @checked(old('is_published', $vacancy->is_published))> Show on the website</label>
    <div><button class="btn" type="submit">Save vacancy</button></div>
  </form>
  @if ($vacancy->exists)
  <form method="POST" action="{{ route('admin.vacancies.destroy', $vacancy) }}" class="danger-zone" data-confirm="Delete this vacancy? Applications for it are kept.">
    @csrf @method('DELETE')
    <button class="btn btn--danger" type="submit">Delete vacancy</button>
  </form>
  @endif
</div>
<script src="{{ asset('js/admin.js') }}"></script>
@endsection
