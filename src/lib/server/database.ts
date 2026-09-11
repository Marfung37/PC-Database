import { DEFAULT_KICKTABLE, DEFAULT_HOLD_TYPE } from '$lib/constants';
import type { Queue, SetupID } from '$lib/types';

const PAGE_SIZE = 100;

export async function getDatabaseSetups(
  supabase: App.Locals['supabase'],
  pc?: number,
  leftover?: Queue,
  cursor?: SetupID,
  limit: number = PAGE_SIZE
) {
  let query = supabase
    .from('setups')
    .select('setup_id, pc, leftover, build, fumen, statistics!inner(solve_percent)')
    .eq('statistics.hold_type', DEFAULT_HOLD_TYPE)
    .eq('statistics.kicktable', DEFAULT_KICKTABLE);

  if (pc) {
    query = query.eq('pc', pc);
  }
  if (leftover) {
    query = query.eq('leftover', leftover);
  }
  if (cursor) {
    query = query.gt('setup_id', cursor);
  }
  query = query.order('setup_id').limit(limit + 1);

  const { data, error } = await query;

  if (error) {
    return { data: null, hasMore: false, error };
  }

  const hasMore = data.length == limit + 1;

  // flatten statistics table
  const cleanData = data.slice(0, Math.min(data.length, limit)).map((row) => {
    return {
      setup_id: row.setup_id,
      pc: row.pc,
      leftover: row.leftover,
      build: row.build,
      fumen: row.fumen,
      solve_percent: row.statistics[0].solve_percent
    };
  });

  return { data: cleanData, hasMore, error: null };
}
