@extends('admin.layout')
@section('title', 'Enquiries')
@section('content')
<div class="head">
  <h1>Enquiries</h1>
  <p class="muted">Quotation and general enquiries from the website's Contact page. Each one is also emailed to {{ config('portal.enquiry_email') }}.</p>
</div>

<nav class="tabs" aria-label="Filter by status">
  <a href="{{ route('admin.enquiries.index', array_filter(['q' => $filters['q'] ?? null])) }}" @class(['on' => empty($filters['status'])])>All <span>{{ $counts->sum() }}</span></a>
  @foreach (\App\Models\Enquiry::STATUSES as $key => $label)
    <a href="{{ route('admin.enquiries.index', array_filter(['status' => $key, 'q' => $filters['q'] ?? null])) }}" @class(['on' => ($filters['status'] ?? '') === $key])>{{ $label }} <span>{{ $counts[$key] ?? 0 }}</span></a>
  @endforeach
</nav>

<form method="GET" class="filters">
  @if (!empty($filters['status']))<input type="hidden" name="status" value="{{ $filters['status'] }}">@endif
  <label>Search <input type="search" name="q" value="{{ $filters['q'] ?? '' }}" placeholder="Name, company, email or service"></label>
  <button class="btn btn--ghost" type="submit">Filter</button>
</form>

@if ($enquiries->isEmpty())
  <p class="empty">No enquiries found.</p>
@else
<div class="table-wrap">
<table>
  <thead><tr><th>Received</th><th>From</th><th>Service</th><th>Status</th></tr></thead>
  <tbody>
  @foreach ($enquiries as $e)
    <tr>
      <td>{{ $e->created_at->timezone('Asia/Kuching')->format('j M Y') }}</td>
      <td><a href="{{ route('admin.enquiries.show', $e) }}">{{ $e->company ?: $e->name }}</a><br><span class="muted small">{{ $e->company ? $e->name.' · ' : '' }}{{ $e->email }}</span></td>
      <td>{{ $e->service ?: 'General' }}</td>
      <td><span class="pill pill--{{ $e->status }}">{{ $e->statusLabel() }}</span></td>
    </tr>
  @endforeach
  </tbody>
</table>
</div>
{{ $enquiries->links('admin.pagination') }}
@endif
@endsection
