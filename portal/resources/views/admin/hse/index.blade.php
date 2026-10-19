@extends('admin.layout')
@section('title', 'HSE figures')
@section('content')
<div class="head head--split">
  <div>
    <h1>HSE figures</h1>
    <p class="muted">Published figures appear on the website's Home and HSE pages, with their "as of" date. Update them each month.</p>
  </div>
  <a class="btn" href="{{ route('admin.hse.create') }}">Add figure</a>
</div>
@if ($figures->isEmpty())
  <p class="empty">No figures yet. Add one such as "1.2 million" / "Man-hours without lost-time injury".</p>
@else
<div class="table-wrap">
<table>
  <thead><tr><th>Figure</th><th>As of</th><th>On website</th><th>Order</th></tr></thead>
  <tbody>
  @foreach ($figures as $f)
    <tr>
      <td><a href="{{ route('admin.hse.edit', $f) }}"><strong>{{ $f->value }}</strong> {{ $f->label }}</a>@if ($f->detail)<br><span class="muted small">{{ $f->detail }}</span>@endif</td>
      <td>{{ $f->as_of->format('j M Y') }}@if ($f->as_of->lt(now()->subMonths(2)->startOfMonth()))<br><span class="pill pill--rejected">Out of date</span>@endif</td>
      <td>@if ($f->is_published)<span class="pill pill--hired">Showing</span>@else<span class="pill">Hidden</span>@endif</td>
      <td>{{ $f->sort_order }}</td>
    </tr>
  @endforeach
  </tbody>
</table>
</div>
@endif
@endsection
