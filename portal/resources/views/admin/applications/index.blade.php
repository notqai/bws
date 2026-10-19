@extends('admin.layout')
@section('title', 'Applications')
@section('content')
<div class="head">
  <h1>Job applications</h1>
  <p class="muted">Applications and CVs are deleted automatically after {{ config('portal.retention_months') }} months.</p>
</div>

<nav class="tabs" aria-label="Filter by status">
  <a href="{{ route('admin.applications.index', array_filter(['vacancy' => $filters['vacancy'] ?? null, 'q' => $filters['q'] ?? null])) }}" @class(['on' => empty($filters['status'])])>All <span>{{ $counts->sum() }}</span></a>
  @foreach (\App\Models\JobApplication::STATUSES as $key => $label)
    <a href="{{ route('admin.applications.index', array_filter(['status' => $key, 'vacancy' => $filters['vacancy'] ?? null, 'q' => $filters['q'] ?? null])) }}" @class(['on' => ($filters['status'] ?? '') === $key])>{{ $label }} <span>{{ $counts[$key] ?? 0 }}</span></a>
  @endforeach
</nav>

<form method="GET" class="filters">
  @if (!empty($filters['status']))<input type="hidden" name="status" value="{{ $filters['status'] }}">@endif
  <label>Vacancy
    <select name="vacancy">
      <option value="">All vacancies</option>
      @foreach ($vacancies as $v)
        <option value="{{ $v->id }}" @selected(($filters['vacancy'] ?? '') == $v->id)>{{ $v->title }} ({{ $v->location }})</option>
      @endforeach
    </select>
  </label>
  <label>Search <input type="search" name="q" value="{{ $filters['q'] ?? '' }}" placeholder="Name, email or position"></label>
  <button class="btn btn--ghost" type="submit">Filter</button>
</form>

@if ($applications->isEmpty())
  <p class="empty">No applications found.</p>
@else
<div class="table-wrap">
<table>
  <thead><tr><th>Received</th><th>Name</th><th>Position</th><th>Experience</th><th>Status</th></tr></thead>
  <tbody>
  @foreach ($applications as $a)
    <tr>
      <td>{{ $a->created_at->timezone('Asia/Kuching')->format('j M Y') }}</td>
      <td><a href="{{ route('admin.applications.show', $a) }}">{{ $a->name }}</a><br><span class="muted small">{{ $a->email }}</span></td>
      <td>{{ $a->position }}</td>
      <td>{{ $a->years_experience !== null ? $a->years_experience.' yrs' : '-' }}</td>
      <td><span class="pill pill--{{ $a->status }}">{{ $a->statusLabel() }}</span></td>
    </tr>
  @endforeach
  </tbody>
</table>
</div>
{{ $applications->links('admin.pagination') }}
@endif
@endsection
