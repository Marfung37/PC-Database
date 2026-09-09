import { json } from '@sveltejs/kit';

export async function GET({ url, locals: { supabase } }) {
  const cursor = url.searchParams.get('cursor');

  let query = supabase
    .from('setups')
    .select('setup_id, pc, leftover, build, fumen')
    .order('setup_id')
    .limit(21);

  if (cursor) {
    query = query.gt('setup_id', cursor);
  }

  const { data, error } = await query;

  if (error) {
    return json({ error: error.message }, { status: 500 });
  }

  const hasMore = data.length > 20;

  if (hasMore) {
    data.pop();
  }

  return json({
    setups: data,
    hasMore,
    cursor: data.at(-1)?.setup_id ?? cursor
  });
}
