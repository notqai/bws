@extends('admin.layout')
@section('title', $figure->exists ? 'Edit HSE figure' : 'Add HSE figure')
@section('content')
<p><a href="{{ route('admin.hse.index') }}">&larr; All HSE figures</a></p>
<div class="card">
  <h1>{{ $figure->exists ? 'Edit HSE figure' : 'Add HSE figure' }}</h1>
  <p class="muted">Only publish figures BWS can back up with its HSE records. They are shown exactly as typed.</p>
  @if ($errors->any())<p class="error" role="alert">Please check the highlighted fields.</p>@endif
  <form method="POST" action="{{ $figure->exists ? route('admin.hse.update', $figure) : route('admin.hse.store') }}" class="stack">
    @csrf
    @if ($figure->exists) @method('PUT') @endif
    <div class="row">
      <label>Figure <input name="value" value="{{ old('value', $figure->value) }}" required maxlength="40" placeholder="e.g. 1.2 million">@error('value')<span class="error">{{ $message }}</span>@enderror</label>
      <label>Label <input name="label" value="{{ old('label', $figure->label) }}" required maxlength="120" placeholder="e.g. Man-hours without lost-time injury">@error('label')<span class="error">{{ $message }}</span>@enderror</label>
    </div>
    <div class="row">
      <label>Detail <span class="muted small">(optional)</span><input name="detail" value="{{ old('detail', $figure->detail) }}" maxlength="200" placeholder="e.g. All active projects, since Jan 2024"></label>
      <label>As of <input type="date" name="as_of" value="{{ old('as_of', $figure->as_of?->toDateString()) }}" required>@error('as_of')<span class="error">{{ $message }}</span>@enderror</label>
      <label>Order <input type="number" name="sort_order" min="0" max="999" value="{{ old('sort_order', $figure->sort_order ?? 0) }}"></label>
    </div>
    <label class="check"><input type="checkbox" name="is_published" value="1" @checked(old('is_published', $figure->is_published))> Show on the website</label>
    <div><button class="btn" type="submit">Save figure</button></div>
  </form>
  @if ($figure->exists)
  <form method="POST" action="{{ route('admin.hse.destroy', $figure) }}" class="danger-zone" data-confirm="Delete this HSE figure?">
    @csrf @method('DELETE')
    <button class="btn btn--danger" type="submit">Delete figure</button>
  </form>
  @endif
</div>
<script src="{{ asset('js/admin.js') }}"></script>
@endsection
