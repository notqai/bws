@extends('admin.layout')
@section('title', $enquiry->company ?: $enquiry->name)
@section('content')
<p><a href="{{ route('admin.enquiries.index') }}">&larr; All enquiries</a></p>
<div class="head">
  <h1>{{ $enquiry->company ?: $enquiry->name }}</h1>
  <p class="muted">{{ $enquiry->service ?: 'General enquiry' }}, received {{ $enquiry->created_at->timezone('Asia/Kuching')->format('j M Y, g:i a') }}</p>
</div>

<div class="grid">
  <section class="card">
    <h2>Details</h2>
    <dl class="details">
      <dt>Name</dt><dd>{{ $enquiry->name }}</dd>
      <dt>Company</dt><dd>{{ $enquiry->company ?: '-' }}</dd>
      <dt>Email</dt><dd><a href="mailto:{{ $enquiry->email }}?subject={{ rawurlencode('Re: your enquiry to BWS Engineering') }}">{{ $enquiry->email }}</a></dd>
      <dt>Phone</dt><dd>@if ($enquiry->phone)<a href="tel:{{ preg_replace('/[^0-9+]/', '', $enquiry->phone) }}">{{ $enquiry->phone }}</a>@else - @endif</dd>
      <dt>Service</dt><dd>{{ $enquiry->service ?: '-' }}</dd>
    </dl>
    <h3>Message</h3>
    <p class="message">{{ $enquiry->message }}</p>
  </section>

  <section class="card">
    <h2>Follow-up</h2>
    <form method="POST" action="{{ route('admin.enquiries.update', $enquiry) }}" class="stack">
      @csrf @method('PATCH')
      <label>Status
        <select name="status">
          @foreach (\App\Models\Enquiry::STATUSES as $key => $label)
            <option value="{{ $key }}" @selected($enquiry->status === $key)>{{ $label }}</option>
          @endforeach
        </select>
      </label>
      <label>Internal notes <textarea name="notes" rows="6" placeholder="Quotation reference, who is handling it, next step">{{ old('notes', $enquiry->notes) }}</textarea></label>
      <button class="btn" type="submit">Save</button>
    </form>

    <form method="POST" action="{{ route('admin.enquiries.destroy', $enquiry) }}" class="danger-zone" data-confirm="Delete this enquiry permanently?">
      @csrf @method('DELETE')
      <p class="muted small">Delete spam, or when the sender asks you to remove their details.</p>
      <button class="btn btn--danger" type="submit">Delete enquiry</button>
    </form>
  </section>
</div>
<script src="{{ asset('js/admin.js') }}"></script>
@endsection
