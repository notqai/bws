@extends('admin.layout')
@section('title', 'Vacancies')
@section('content')
<div class="head head--split">
  <div>
    <h1>Vacancies</h1>
    <p class="muted">Published vacancies appear on the website's Careers page until their closing date.</p>
  </div>
  <a class="btn" href="{{ route('admin.vacancies.create') }}">Add vacancy</a>
</div>
@if ($vacancies->isEmpty())
  <p class="empty">No vacancies yet. The Careers page shows the "Send your CV" option on its own.</p>
@else
<div class="table-wrap">
<table>
  <thead><tr><th>Position</th><th>Location</th><th>Closes</th><th>On website</th><th>Applications</th></tr></thead>
  <tbody>
  @foreach ($vacancies as $v)
    <tr>
      <td><a href="{{ route('admin.vacancies.edit', $v) }}">{{ $v->title }}</a>@if ($v->discipline)<br><span class="muted small">{{ $v->discipline }}</span>@endif</td>
      <td>{{ $v->location }}</td>
      <td>{{ $v->closes_on?->format('j M Y') ?? 'Open' }}</td>
      <td>@if ($v->isOpen())<span class="pill pill--hired">Showing</span>@elseif ($v->is_published)<span class="pill">Closed</span>@else<span class="pill">Draft</span>@endif</td>
      <td><a href="{{ route('admin.applications.index', ['vacancy' => $v->id]) }}">{{ $v->applications_count }}</a></td>
    </tr>
  @endforeach
  </tbody>
</table>
</div>
@endif
@endsection
