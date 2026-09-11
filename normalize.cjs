function normalize(items) {
  const accepted = [], rejected = [], seen = new Set();
  for (let index = 0; index < items.length; index++) {
    const data = items[index];
    const fail = reason => rejected.push({ index, reason });
    if (!data || typeof data !== 'object' || Array.isArray(data)) { fail('invalid_object'); continue; }
    if (typeof data.requestId !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(data.requestId)) { fail('invalid_request_id'); continue; }
    if (typeof data.email !== 'string' || data.email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email.trim())) { fail('invalid_email'); continue; }
    if (typeof data.name !== 'string' || !data.name.trim() || data.name.length > 160) { fail('invalid_name'); continue; }
    if (seen.has(data.requestId)) { fail('duplicate_request_id'); continue; }
    seen.add(data.requestId);
    accepted.push({ externalId: data.requestId, name: data.name.trim(), email: data.email.trim().toLowerCase(), source: 'demo-form' });
  }
  return { accepted, rejected };
}
module.exports = { normalize };
