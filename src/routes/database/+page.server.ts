import { redirect } from '@sveltejs/kit';
import { fail } from '@sveltejs/kit';
import { isQueue } from '$lib/utils/queueUtils';
import { getDatabaseSetups } from '$lib/server/database.js';
import { formAction, setupIDSchema, pcSchema, queueSchema } from '$lib/server/forms';
import { z } from 'zod';
import type { Actions, PageServerLoad } from './$types';
import type { Queue } from '$lib/types';

interface FilterOptions {
  pc?: number;
  leftover?: Queue;
}

export const load: PageServerLoad = async function ({ url, locals: { supabase }, depends }) {
  depends('setups');

  const params = url.searchParams;
  const filters = normalizeParams(params);

  if (filters === null) redirect(307, `${url.pathname}?${params.toString()}`);

  // query to list of leftovers
  let leftoverQuery = supabase.from('pc_leftovers').select('leftover');

  if (filters.pc) {
    leftoverQuery = leftoverQuery.eq('pc', filters.pc);
  }
  leftoverQuery = leftoverQuery.order('sort_key');

  const { data, hasMore, error } = await getDatabaseSetups(supabase, filters.pc, filters.leftover);

  if (error) {
    console.error(`Failed to get setup data: ${error.message}`);
    return fail(500, {
      message: `Failed to get setup data`
    });
  }

  let leftovers: string[] = [];
  if (filters.pc) {
    const { data: leftoverData, error: leftoverErr } = await leftoverQuery;

    if (leftoverErr) {
      console.error(`Failed to get list of leftovers: ${leftoverErr.message}`);
      return fail(500, {
        message: `Failed to get leftover data`
      });
    }

    leftovers = leftoverData.map((row) => row.leftover);
  }

  return { setups: data, hasMore, leftovers };
};

function normalizeParams(params: URLSearchParams): FilterOptions | null {
  const rawPC = params.get('pc');
  const rawLeftover = params.get('leftover');

  const options: FilterOptions = {};
  if (rawPC !== null) {
    const parsedPC = Number(rawPC);

    if (!Number.isInteger(parsedPC) || parsedPC < 1 || parsedPC > 9) {
      params.delete('pc');
    } else {
      options.pc = parsedPC;
    }
  }

  if (rawLeftover !== null) {
    if (!isQueue(rawLeftover)) {
      params.delete('leftover');
    } else {
      options.leftover = rawLeftover as Queue;
    }
  }

  return options;
}

const loadMoreSchema = z.object({
  pc: z.preprocess((value) => (value === '' ? undefined : value), pcSchema.optional()),
  leftover: z.preprocess((value) => (value === '' ? undefined : value), queueSchema.optional()),
  cursor: setupIDSchema
});

export const actions: Actions = {
  loadMore: formAction(
    loadMoreSchema,
    async ({ data: { pc, leftover, cursor }, locals: { supabase } }) => {
      const { data, hasMore, error } = await getDatabaseSetups(supabase, pc, leftover, cursor);

      if (error) {
        console.error('Failed to load more setups:', error.message);
        return fail(500, {
          error: 'Failed to load more setups'
        });
      }

      return { setups: data, hasMore };
    }
  )
};
